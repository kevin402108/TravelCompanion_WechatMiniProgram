import datetime
import json
import os
import time
import requests
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from pymysql import DataError, IntegrityError, OperationalError, ProgrammingError
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from backEnd.app.database import get_database
from backEnd.app.models import Login, User
from backEnd.app.utils.crypt import encrypt
from backEnd.app.utils.logger import setup_logger

user_account_logger = setup_logger('user_account_logger') # 用户帐户操作相关行为日志
account_router = APIRouter() # 用户帐户操作路由

# 注册请求数据模型
class RegisterRequest(BaseModel):
    code: str

# 登录请求数据模型
class LoginRequest(BaseModel):
    id: int
    code: str

# 用户登录API PUT请求
@account_router.put('/auth/login/')
def login(
        loginRequest: LoginRequest,
        db: Session = Depends(get_database)
):
    # 判断用户ID是否存在且有效
    if not loginRequest.id:
        user_account_logger.error("更新登录时间请求中用户ID为空")
        raise HTTPException(status_code=400, detail="用户ID不能为空!")
    if loginRequest.id <=0:
        user_account_logger.error("更新登录时间请求中用户ID无效")
        raise HTTPException(status_code=400, detail="用户ID无效!")
    user_id = loginRequest.id # 符合要求的用户ID
    
    try:
        user_account_logger.info(f"用户登录请求: 用户ID={user_id}")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user_account_logger.error(f"用户不存在: 用户ID={user_id}")
            raise HTTPException(status_code=404, detail=f"无法查询到用户:用户ID={user_id}")
        
        if not loginRequest.code:
            user_account_logger.error("登录请求中登录code为空")
            raise HTTPException(status_code=400, detail="登录请求中code不能为空")
        login_code = loginRequest.code
        
        url = f"https://api.weixin.qq.com/sns/jscode2session?appid=wxa35b788e7a7760be&secret=8ca4524d10d633e14e34ba449b0e0ef0&js_code={login_code}&grant_type=authorization_code"
        user_account_logger.info("调用微信API获取用户信息")
        result = requests.get(url)
        result.raise_for_status()

        data = result.json()
        openid = data["openid"]
        session_key = data["session_key"]

        iat = time.time() # 当前时间戳
        token = f"token-{openid}-{int(iat)}" # 生成token
        # key = os.urandom(32) # 随机32字节密钥
        # iv = os.urandom(16) # 随机16字节初始向量
        # encrypted_token = encrypt(token, key, iv) # 加密token


        db.query(Login).filter(Login.user_id == user_id).update({
            "openid": openid,
            "session_key": session_key,
            "token": token,
            "last_login_time": datetime.datetime.now(),
            "login_source": "wechat"
        })
        db.commit()
        user_account_logger.info(f"用户登录成功: ID={user_id}")

        response = {
            "data": {
                "id": user_id,
                "token": token
            }
        }
        return response
    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        user_account_logger.error(f"微信API请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"用户ID={user_id}登录失败:微信API调用失败:,")
    except json.JSONDecodeError as e:
        user_account_logger.error(f"JSON解析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"JSON解析失败: {str(e)}")
    except KeyError as e:
        user_account_logger.error(f"微信API返回数据缺少必要字段: {str(e)}")
        raise HTTPException(status_code=500, detail=f"KeyError: {str(e)}")
    except OperationalError as e:
        user_account_logger.error(f"数据库操作异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"用户登录时数据库连接错误：ID={user_id}")
    except ProgrammingError as e:
        user_account_logger.error(f"SQL语句执行异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SQL执行错误: {str(e)}")
    except DataError as e:
        user_account_logger.error(f"数据类型不匹配: {str(e)}")
        raise HTTPException(status_code=500, detail=f"数据类型不匹配错误: {str(e)}")
    except IntegrityError as e:
        db.rollback()
        user_account_logger.error(f"完整性约束异常: {str(e)}")
        raise HTTPException(status_code=409, detail=f"违反完整性约束错误: {str(e)}")
    except Exception as e:
        if db.is_active:
            db.rollback()
        user_account_logger.error(f"用户ID={user_id}登录时遇到未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"用户ID={user_id}登录时遇到未知错误: {str(e)}")

# 更新用户登录时间请求数据模型
class UpdateUserLoginTimeRequest(BaseModel):
    id: int

# 更新登录时间API PUT请求
@account_router.put('/user/updateLoginTime')
def updateLoginTime(
        updateUserLoginTimeRequest: UpdateUserLoginTimeRequest,
        db: Session = Depends(get_database)
):  
    if updateUserLoginTimeRequest.id is None:
        user_account_logger.error("更新登录时间请求中缺少用户ID或用户ID为空")
        raise HTTPException(status_code=400, detail="更新登录时间请求中缺少用户ID或用户ID为空!")
    if updateUserLoginTimeRequest.id <= 0:
        user_account_logger.error("更新登录时间请求中用户ID小于1，用户ID无效")
        raise HTTPException(status_code=422, detail="用户ID无效!")
    user_id = updateUserLoginTimeRequest.id  # 符合要求的用户ID
    
    try:
        user_account_logger.info(f"开始更新用户登录时间")
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.query(Login).filter(Login.user_id == updateUserLoginTimeRequest.id).update({
                "last_login_time": func.now()
            })
            db.commit()
            user_account_logger.info("更新用户登录时间成功")
            return {
                "data": {
                    "message": "更新用户登录时间成功"
                }
            }
        else:
            user_account_logger.error(f"用户不存在: 用户ID={user_id}")
            raise HTTPException(status_code=404, detail=f"无法查询到该用户")
    except HTTPException:
        raise
    except OperationalError as e:
        user_account_logger.error(f"数据库操作异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"数据库连接错误：{str(e)}")
    except ProgrammingError as e:
        user_account_logger.error(f"SQL语句执行异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SQL执行错误: {str(e)}")
    except DataError as e:
        user_account_logger.error(f"数据类型不匹配: {str(e)}")
        raise HTTPException(status_code=500, detail=f"数据类型不匹配错误: {str(e)}")
    except IntegrityError as e:
        db.rollback()
        user_account_logger.error(f"完整性约束异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"违反完整性约束错误: {str(e)}")
    except Exception as e:
        if db.is_active:
            db.rollback()
        user_account_logger.error(f"更新用户ID={user_id}登录时间时遇到未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新用户ID={user_id}登录时间时遇到未知错误: {str(e)}")

# 用户注册API POST请求
@account_router.post("/auth/register")
def register(registerCode: RegisterRequest, db: Session = Depends(get_database)):
    try:
        user_account_logger.info("开始进行用户注册")
        register_code = registerCode.code
        if not register_code:
            user_account_logger.error("注册请求中code为空")
            raise HTTPException(status_code=400, detail="注册请求中code不能为空")
        
        # 调用微信API获取openid、session_key
        user_account_logger.info("调用微信API获取openid、session_key")
        url = f"https://api.weixin.qq.com/sns/jscode2session?appid=wxa35b788e7a7760be&secret=8ca4524d10d633e14e34ba449b0e0ef0&js_code={registerCode.code}&grant_type=authorization_code"
        result = requests.get(url)
        result.raise_for_status()
        
        data = result.json() 
        openid = data["openid"] # 获取openid
        session_key = data["session_key"] # 获取session_key
        iat = time.time() # 获取当前时间戳
        token = f"token-{openid}-{int(iat)}" # 生成token
        # key = os.urandom(32) # 生成随机32字节密钥
        # iv = os.urandom(16) # 生成随机16字节初始向量
        # encrypted_session_key = encrypt(session_key, key, iv) # 加密session_key
        # encrypted_token = encrypt(token, key, iv) # 加密token
        
        # 检查用户openid是否已存在，防止因缓存清除等原因而重复注册
        user_account_logger.info("正在检查用户是否重复注册……")
        existing_user = db.query(Login).filter(Login.openid == openid).first()
        
        # 如果用户已存在,则只更新登录信息，不再创建新用户
        if existing_user:
            user_id = existing_user.user_id
            user_account_logger.info(f"用户已存在:ID={user_id},无需重复注册,正在更新用户登录信息")
            db.query(Login).filter(Login.user_id == user_id).update({
                "session_key": session_key,
                "token": token,
                "last_login_time": func.now(),
                "login_source": "wechat"
            })
            db.commit()
            user_account_logger.info(f"用户登录信息更新成功:ID={user_id}")
        
        # 若用户不存在，则创建新用户和登录记录
        else:
            new_user = User(gender=None, hobby=None)
            db.add(new_user)
            db.flush()
            id = new_user.id
            login_record = Login(
                user_id=new_user.id,
                openid=openid,
                session_key=session_key,
                token=token
            )
            db.add(login_record)
            db.commit()
            user_account_logger.info(f"用户注册成功:ID={id}")
        
        is_new_user = existing_user is None # 标记是否为新用户
        response = {
            "data": {
                "isNewUser": is_new_user,
                "token": token,
                "message": "用户注册成功" if is_new_user else "用户登录信息已更新"
            }
        }
        return response
    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        user_account_logger.error(f"微信API请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"微信API调用失败: {str(e)}")
    except json.JSONDecodeError as e:
        user_account_logger.error(f"JSON解析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"JSON解析失败: {str(e)}")
    except KeyError as e:
        user_account_logger.error(f"微信API返回数据缺少必要字段: {str(e)}")
        raise HTTPException(status_code=500, detail=f"KeyError: {str(e)}")
    except IntegrityError as e:
        db.rollback()
        user_account_logger.error(f"数据库约束错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"违反完整性约束错误: {str(e)}")
    except DataError as e:
        db.rollback()
        user_account_logger.error(f"数据库数据类型错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"数据错误: {str(e)}")
    except Exception as e:
        if db.is_active:
            db.rollback()
        user_account_logger.error(f"注册过程未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"未知错误: {str(e)}")
    



