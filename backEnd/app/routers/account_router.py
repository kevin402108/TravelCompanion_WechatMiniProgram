import os
import pytz
import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException,Request
from pydantic import BaseModel
from backEnd.app.database import get_database
from backEnd.app.models import User
from backEnd.app.utils.encryption import encrypt,decrypt,get_key
from backEnd.app.utils.jwt_handler import createUserToken
from backEnd.app.utils.logger import setupLogger

userAccountLogger = setupLogger( 'user_account_logger' , fileName= 'user_account_behavior.log' )
account_router = APIRouter()

# 一般配置
TZ = pytz.timezone('Asia/Shanghai')
WX_APPID = os.getenv('WX_APPID')
WX_APP_SEC = os.getenv('WX_APP_SEC')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 15))

# 请求数据模型
class RegisterRequest(BaseModel):
    code: str

class LoginRequest(BaseModel):
    code: str

def getWechatUserInfo( code:str ) -> dict:
    """ 调用微信API获取用户信息 """
    if not isinstance(code, str) or not code.strip():
        userAccountLogger.error( "[getWechatUserInfo] code参数不为非空字符串" )
        raise HTTPException(status_code=400, detail="微信登录凭证 (code) 无效：code必须是非空字符串!")

    if not WX_APPID or not WX_APP_SEC:
        userAccountLogger.error( "[getWechatUserInfo] 微信小程序获取配置错误" )
        raise HTTPException(status_code=500, detail="微信小程序获取配置错误")

    userAccountLogger.info( "调用微信API获取openid、session_key" )
    url = f"https://api.weixin.qq.com/sns/jscode2session?appid={WX_APPID}&secret={WX_APP_SEC}&js_code={code}&grant_type=authorization_code"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "errcode" in data:
            error_msg = data.get('errmsg','未知错误')
            userAccountLogger.error( f"[getWechatUserInfo] 微信API错误: {data[ 'errcode' ]}-{error_msg}" )
            raise HTTPException(status_code=data["errcode"], detail=error_msg)
        openid = data.get('openid')
        if not openid:
            userAccountLogger.error( "[getWechatUserInfo] 未返回openid" )
            raise HTTPException(status_code=400, detail="未能获取用户openid")
        userAccountLogger.info( f"[getWechatUserInfo] 成功获取用户openid" )
        return {
            "openid": openid
        }
    except requests.exceptions.RequestException as re:
        userAccountLogger.error( f"[getWechatUserInfo] 微信API请求失败: {str( re )}" )
        raise HTTPException(status_code=500, detail=f"微信API请求失败:  {str(re)}")
    except ValueError as ve:
        userAccountLogger.error( f"[getWechatUserInfo] JSON解析失败: {str( ve )}" )
        raise HTTPException(status_code=500, detail=f"JSON解析失败: {str(ve)}")
    except Exception as e:
        userAccountLogger.error( f"[getWechatUserInfo] 获取微信用户信息时发生未知错误: {str( e )}" )
        raise HTTPException(status_code=500, detail=f"获取用户信息时发生未知错误: {str(e)}")

def isOpenidExists(db:Session,openid:str):
    """ 检查给定的 openid 是否已存在于数据库中（通过比较解密后的值）"""
    try:
        login_records = db.query(User).filter(User.openid.isnot(None)).all()
        for record in login_records:
            try:
                decrypted_openid = decrypt(record.openid)
                if decrypted_openid == openid:
                    return record
            except Exception as decrypt_error:
                userAccountLogger.error( f"[isOpenidExists] 解密 openid 失败: {str( decrypt_error )}, 记录ID: {record.id}" )
                continue
        return None
    except Exception as e:
        userAccountLogger.error( f"[isOpenidExists] 检查openid是否存在时发生错误: {str( e )}" )
        return None

@account_router.post("/users")
def register(request:LoginRequest,db:Session = Depends(get_database),req:Request=None):
    client_ip = req.client.host if req else "unknown"
    userAccountLogger.info( f"[register] 接收到注册请求，IP: {client_ip}" )

    if not isinstance(request.code, str) or not request.code.strip():
        userAccountLogger.error( "[register] 登录凭证 (code) 为空" )
        raise HTTPException(status_code=400, detail="微信登录凭证 (code) 不能为空")

    try:
        wechat_user_info = getWechatUserInfo( request.code )
        openid = wechat_user_info.get("openid")
        encrypt_openid = encrypt(openid)

        existing_user = isOpenidExists ( db , openid )
        if existing_user:
            userAccountLogger.info( f"[register] 找到用户，开始认证" )
            user_id = existing_user.id
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            token_data = {"user_id": user_id,"openid":openid}
            access_token = createUserToken( data=token_data , expires_delta=access_token_expires )
            try:
                existing_user.openid = encrypt_openid
                existing_user.last_login_time = datetime.now(TZ)
                db.commit()
            except Exception as e:
                userAccountLogger.error( f"[register] 更新用户信息时发生错误: {str( e )}" )
                db.rollback()
                raise HTTPException(status_code=500, detail=f"更新用户信息时发生错误: {str(e)}")

            # 计算过期时间戳
            exp_timestamp = datetime.now(TZ) + access_token_expires
            exp_timestamp = int(exp_timestamp.timestamp())

            userAccountLogger.info( f"[register] 老用户认证成功" )
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
                userAccountLogger.error( f"[register] 新用户注册时发生错误: {str( e )}" )
                db.rollback()
                raise HTTPException(status_code=500, detail=f"新用户注册时发生错误: {str(e)}")

            userAccountLogger.info( f"[register] 新用户注册成功" )
            return {
                "data":{
                    "success":True,
                    "isNewUser":True,
                }
            }
    except HTTPException:
         raise
    except Exception as e:
        userAccountLogger.error( f"[register] 认证过程中发生错误 - {str( e )}" )
        raise HTTPException(status_code=500, detail=f"认证过程中发生错误 - {str(e)}")

@account_router.post("/sessions")
def createSession(request:LoginRequest,db:Session = Depends(get_database),req:Request=None):
    """ 为新用户签发JWT token """
    client_ip = req.client.host if req else "unknown"
    userAccountLogger.info( f"[createSession] 接收到登录请求，IP: {client_ip}" )

    if not isinstance(request.code, str) or not request.code.strip():
        userAccountLogger.error( "[createSession] 登录凭证 (code) 为空" )
        raise HTTPException(status_code=400, detail="登录凭证不能为空")

    try:
        wechat_user_info = getWechatUserInfo( request.code )
        openid = wechat_user_info.get("openid")

        # 检查用户是否存在
        existing_user = isOpenidExists ( db , openid )
        if not existing_user:
            userAccountLogger.error( "[createSession] 用户不存在" )
            raise HTTPException(status_code=404, detail="用户不存在!")

        #  签发JWT token
        user_id = existing_user.id
        encrypt_openid = encrypt(openid)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"user_id": user_id,"openid":openid}
        access_token = createUserToken( data=token_data , expires_delta=access_token_expires )

        try:
            existing_user.last_login_time = datetime.now(TZ)
            db.commit()
            db.refresh(existing_user)
        except Exception as e:
            userAccountLogger.error( f"[createSession] 用户登录时发生错误: {str( e )}" )
            db.rollback()
            raise HTTPException(status_code=500, detail=f"用户登录时发生错误: {str(e)}")

        exp_timestamp = datetime.now(TZ) + access_token_expires
        exp_timestamp = int(exp_timestamp.timestamp())

        userAccountLogger.info( f"[createSession] 登录成功" )
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
        userAccountLogger.error( f"[createSession] 登录过程中发生错误 - {str( e )}" )
        raise HTTPException(status_code=500, detail=f"登录过程中发生错误 - {str(e)}")



