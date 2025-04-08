import datetime
import json
import os
import time
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import backEnd.app.utils.exceptions as exceptions
from pymysql import DataError, IntegrityError, OperationalError, ProgrammingError
import requests
from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel, Field

from backEnd.app.database import get_database
from backEnd.app.models import Login, User
from backEnd.app.utils.crypt import encrypt
from backEnd.app.utils.logger import setup_logger
from backEnd.app.utils.user import checkUserExist

#登录模块路由
logger = setup_logger('user_login')
login_router = APIRouter()

class RegisterRequest(BaseModel):
    code:str

class LoginRequest(BaseModel):
    id: int
    code: str
    
# 登录接口 POST请求
@login_router.put('/auth/login/')
def login(loginCode: LoginRequest,db:Session=Depends(get_database)):
    try:
        id = loginCode.id
        queryResult = checkUserExist(id)
        if not queryResult[0]:
            raise exceptions.UserNotFoundError()

        url = f"https://api.weixin.qq.com/sns/jscode2session?appid=wxa35b788e7a7760be&secret=8ca4524d10d633e14e34ba449b0e0ef0&js_code={loginCode.code}&grant_type=authorization_code"
        result = requests.get(url)
        result.raise_for_status()

        data = result.json()
        openid = data["openid"]
        session_key = data["session_key"]

        iat = time.time()  # iat token创建时间
        token = f"token-{openid}-{int(iat)}"
        key = os.urandom(32)
        iv = os.urandom(16)
        encrypted_token = encrypt(token, key, iv)  # 将加密的token后转化base64字符串

        db.query(Login).filter(Login.user_id == id).update({
            "openid": openid,
            "session_key": session_key,
            "token": encrypted_token,
            "last_login_time": datetime.datetime.now(),
            "login_source": "wechat"
        })

        response = {
            "data": {
                "id": id, # 用户id
                "token": encrypted_token,
                "loginStatus": 1  # 登录态 1:已登录 0:未登录
            }
        }

        return response
    except requests.exceptions.RequestException as e:
        # 微信API请求失败，返回503状态码
        raise exceptions.WechatAPIRequestError(str(e))
    except json.JSONDecodeError as e:
        # JSON解析失败，返回500状态码
        raise exceptions.JSONDecodeError(str(e))
    except KeyError as e:
        # 微信API返回数据缺少必要字段，返回500状态码
        raise exceptions.WechatAPIKeyError(str(e))
    except Exception as e:
        # 若数据库操作失败，回滚事务
        if db.is_active:
            db.rollback()
        # 未知错误，返回500状态码
        raise exceptions.UnknownError(str(e))

class UpdateUserId(BaseModel):
    id:int = Field(...,gt=0)


# 更新登录时间接口 PUT请求
@login_router.put('/user/updateLoginTime')
def updateLoginTime(
    userInfo:UpdateUserId,
    db:Session=Depends(get_database)
):
    try:
        queryResult = checkUserExist(userInfo.id)
        if queryResult[0]:
            db.query(Login).filter(Login.user_id==userInfo.id).update({"last_login_time":func.now()})
            db.commit()
            logger.info("更新用户登录时间成功")
            response = {
                "data":{
                    "message":"更新用户登录时间成功"
                }
            }
            return response
        else:
            raise exceptions.UserNotFoundError()
    except OperationalError as e:
        #数据库操作异常，抛出数据库操作异常
        raise exceptions.DatabaseConnectionError(str(e))
    except ProgrammingError as e:
        # 处理 SQL 语句执行异常
        raise exceptions.SQLExecutionError(str(e))
    except DataError as e:
        # 处理数据类型不匹配异常
        raise exceptions.DataMismatchError(str(e))
    except IntegrityError as e:
        # 处理完整性约束异常
        raise exceptions.IntegrityConstraintError(str(e))
    except Exception as e:
        # 若数据库操作失败，回滚事务
        if db.is_active:
            db.rollback()
        # 处理其他未知异常
        raise exceptions.UnknownError(str(e))
    
# 注册接口 POST请求
@login_router.post("/auth/register")
def register(
    registerCode:RegisterRequest,
    db:Session=Depends(get_database)
):
    try:
        url = f"https://api.weixin.qq.com/sns/jscode2session?appid=wxa35b788e7a7760be&secret=8ca4524d10d633e14e34ba449b0e0ef0&js_code={registerCode.code}&grant_type=authorization_code"
        result = requests.get(url)
        result.raise_for_status()

        data = result.json()
        openid = data["openid"]
        session_key = data["session_key"]

        iat = time.time()  # iat token创建时间
        token = f"token-{openid}-{int(iat)}"
        key = os.urandom(32)
        iv = os.urandom(16)
        encrypted_token = encrypt(token, key, iv)  # 将加密的token后转化base64字符串

        new_user = User(gender=None,hobby=None)
        db.add(new_user)
        db.flush()        
        db.commit()
        
        id = new_user.id
        login_record = Login(
            user_id = new_user.id,
            openid = openid,
            session_key = session_key,
            token = token
        )
        
        db.add(login_record)
        db.flush()        
        db.commit()

        response = {
            "data": {
                "id": id, # 用户id
                "token": encrypted_token,
                "loginStatus": 1  # 登录态 1:已登录 0:未登录
            }
        }

        return response
    except requests.exceptions.RequestException as e:
        # 微信API请求失败，返回503状态码
        raise exceptions.WechatAPIRequestError(str(e))
    except json.JSONDecodeError as e:
        # JSON解析失败，返回500状态码
        raise exceptions.JSONDecodeError(str(e))
    except KeyError as e:
        # 微信API返回数据缺少必要字段，返回500状态码
        raise exceptions.WechatAPIKeyError(str(e))
    except IntegrityError as e:
        # 数据库约束错误，返回409状态码
        raise exceptions.IntegrityConstraintError(str(e))
    except DataError as e:
        # 数据库数据类型错误，返回400状态码
        raise exceptions.DataError(str(e))
    except Exception as e:
        # 若数据库操作失败，回滚事务
        if db.is_active:
            db.rollback()
        # 未知错误，返回500状态码
        raise exceptions.UnknownError(str(e))