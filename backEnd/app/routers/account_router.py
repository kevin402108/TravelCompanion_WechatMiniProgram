import hashlib
import os
import uuid
import jwt
import time
import pytz
import requests
import redis.exceptions
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException,Request
from pydantic import BaseModel
from backEnd.app.database import get_database
from backEnd.app.models import User
from backEnd.app.utils.encryption import encrypt,decrypt,get_key
from backEnd.app.utils.jwt_handler import create_user_token
from backEnd.app.utils.logger import setup_logger

# 日志记录器
user_account_logger = setup_logger('user_account_logger', fileName='user_account_behavior.log')

# 路由
account_router = APIRouter()

# 一般配置
TZ = pytz.timezone('Asia/Shanghai')
WX_APPID = "wxa35b788e7a7760be"
WX_APP_SEC = get_key("WX_APP_SEC")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 15))

# 请求数据模型
class RegisterRequest(BaseModel):
    code: str

class LoginRequest(BaseModel):
    code: str

def get_wechat_user_info(code:str) -> dict:
    """ 调用微信API获取用户信息 """
    if not isinstance(code, str) or not code.strip():
        user_account_logger.error("[get_wechat_user_info] code参数不为非空字符串")
        raise HTTPException(status_code=400, detail="微信登录凭证 (code) 无效：code必须是非空字符串!")

    if not WX_APPID or not WX_APP_SEC:
        user_account_logger.error("[get_wechat_user_info] 微信小程序获取配置错误")
        raise HTTPException(status_code=500, detail="微信小程序获取配置错误")

    user_account_logger.info("调用微信API获取openid、session_key")
    url = f"https://api.weixin.qq.com/sns/jscode2session?appid={WX_APPID}&secret={WX_APP_SEC}&js_code={code}&grant_type=authorization_code"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "errcode" in data:
            error_msg = data.get('errmsg','未知错误')
            user_account_logger.error(f"[get_wechat_user_info] 微信API错误: {data['errcode']}-{error_msg}")
            raise HTTPException(status_code=data["errcode"], detail=error_msg)
        openid = data.get('openid')
        if not openid:
            user_account_logger.error("[get_wechat_user_info] 未返回openid")
            raise HTTPException(status_code=400, detail="未能获取用户openid")
        user_account_logger.info(f"[get_wechat_user_info] 成功获取用户openid")
        return {
            "openid": openid
        }
    except requests.exceptions.RequestException as re:
        user_account_logger.error(f"[get_wechat_user_info] 微信API请求失败: {str(re)}")
        raise HTTPException(status_code=500, detail=f"微信API请求失败:  {str(re)}")
    except ValueError as ve:
        user_account_logger.error(f"[get_wechat_user_info] JSON解析失败: {str(ve)}")
        raise HTTPException(status_code=500, detail=f"JSON解析失败: {str(ve)}")
    except Exception as e:
        user_account_logger.error(f"[get_wechat_user_info] 获取微信用户信息时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取用户信息时发生未知错误: {str(e)}")

def is_openid_exists(db:Session,openid:str):
    """ 检查给定的 openid 是否已存在于数据库中（通过比较解密后的值）"""
    try:
        login_records = db.query(User).filter(User.openid.isnot(None)).all()
        for record in login_records:
            try:
                decrypted_openid = decrypt(record.openid)
                if decrypted_openid == openid:
                    return record
            except Exception as decrypt_error:
                user_account_logger.error(f"[is_openid_exists] 解密 openid 失败: {str(decrypt_error)}, 记录ID: {record.id}")
                continue
        return None
    except Exception as e:
        user_account_logger.error(f"[is_openid_exists] 检查openid是否存在时发生错误: {str(e)}")
        return None

@account_router.post("/auth")
def auth(request:LoginRequest,db:Session = Depends(get_database),req:Request=None):
    client_ip = req.client.host if req else "unknown"
    user_account_logger.info(f"[auth] 接收到认证请求，IP: {client_ip}")

    if not isinstance(request.code, str) or not request.code.strip():
        user_account_logger.error("[auth] 登录凭证 (code) 为空")
        raise HTTPException(status_code=400, detail="微信登录凭证 (code) 不能为空")

    try:
        wechat_user_info = get_wechat_user_info(request.code)
        openid = wechat_user_info.get("openid")
        encrypt_openid = encrypt(openid)

        existing_user = is_openid_exists(db,openid)
        if existing_user:
            user_account_logger.info(f"[auth] 找到用户，开始认证")
            user_id = existing_user.id
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            token_data = {"user_id": user_id,"openid":encrypt_openid,}
            access_token = create_user_token(data=token_data,expires_delta=access_token_expires)
            try:
                existing_user.openid = encrypt_openid
                existing_user.last_login_time = datetime.now(TZ)
                db.commit()
            except Exception as e:
                user_account_logger.error(f"[auth] 更新用户信息时发生错误: {str(e)}")
                db.rollback()
                raise HTTPException(status_code=500, detail=f"更新用户信息时发生错误: {str(e)}")

            # 计算过期时间戳
            exp_timestamp = datetime.now(TZ) + access_token_expires
            exp_timestamp = int(exp_timestamp.timestamp())

            user_account_logger.info(f"[auth] 老用户认证成功")
            return {
                "data":{
                    "success":True,
                    "isNewUser":False,
                    "token":access_token,
                    "token_expired_at":exp_timestamp
                }
            }
        else:
            encrypt_openid = encrypt(openid)
            try:
                new_user = User(openid=encrypt_openid,last_login_time=None)
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
            except Exception as e:
                user_account_logger.error(f"[auth] 新用户注册时发生错误: {str(e)}")
                db.rollback()
                raise HTTPException(status_code=500, detail=f"新用户注册时发生错误: {str(e)}")

            user_account_logger.info(f"[auth] 新用户注册成功")
            return {
                "data":{
                    "success":True,
                    "isNewUser":True,
                }
            }
    except HTTPException:
         raise
    except Exception as e:
        user_account_logger.error(f"[auth] 认证过程中发生错误 - {str(e)}")
        raise HTTPException(status_code=500, detail=f"认证过程中发生错误 - {str(e)}")

@account_router.post("/login")
def login(request:LoginRequest,db:Session = Depends(get_database),req:Request=None):
    """ 为新用户签发JWT token """
    client_ip = req.client.host if req else "unknown"
    user_account_logger.info(f"[login] 接收到登录请求，IP: {client_ip}")

    if not isinstance(request.code, str) or not request.code.strip():
        user_account_logger.error("[login] 登录凭证 (code) 为空")
        raise HTTPException(status_code=400, detail="登录凭证不能为空")

    try:
        wechat_user_info = get_wechat_user_info(request.code)
        openid = wechat_user_info.get("openid")

        # 检查用户是否存在
        existing_user = is_openid_exists(db,openid)
        if not existing_user:
            user_account_logger.error("[login] 用户不存在")
            raise HTTPException(status_code=404, detail="用户不存在!")

        #  签发JWT token
        user_id = existing_user.id
        encrypt_openid = encrypt(openid)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"user_id": user_id,"openid":encrypt_openid,}
        access_token = create_user_token(data=token_data,expires_delta=access_token_expires)

        try:
            existing_user.last_login_time = datetime.now(TZ)
            db.commit()
            db.refresh(existing_user)
        except Exception as e:
            user_account_logger.error(f"[login] 用户登录时发生错误: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"用户登录时发生错误: {str(e)}")

        exp_timestamp = datetime.now(TZ) + access_token_expires
        exp_timestamp = int(exp_timestamp.timestamp())

        user_account_logger.info(f"[login] 登录成功")
        return {
            "data":{
                "success":True,
                "isNewUser":False,
                "token":access_token,
                "token_expired_at":exp_timestamp
            }
        }
    except HTTPException as http_error:
        raise
    except Exception as e:
        user_account_logger.error(f"[login] 登录过程中发生错误 - {str(e)}")
        raise HTTPException(status_code=500, detail=f"登录过程中发生错误!")

