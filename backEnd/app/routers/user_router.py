import hashlib
from typing import Dict , Any

from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from pydantic import BaseModel , ValidationError

from backEnd.app.utils.auth_utils import extractUserByVerifyCredential
from backEnd.app.utils.logger import setupLogger
from sqlalchemy.orm import Session
from fastapi import APIRouter , Depends , HTTPException
from backEnd.app.database import get_database
from backEnd.app.models import User

user_router = APIRouter()
userInfoLogger = setupLogger( 'user_info' , fileName= 'user_info.log' )
security_scheme = HTTPBearer()

def getUserInfo( user ):
    """ 获取用户基本信息 """
    if not user:
        userInfoLogger.error( "[get_user_info] 用户信息不存在" )
        return None

    userInfoLogger.info( f"[get_user_info] 获取用户信息成功" )
    return {
        "nickname": user.nickname,
        "avatar": user.avatar,
        "gender": user.gender,
        "hobby": user.hobby
    }
    

@user_router.get('/users/profile')
def getUserProfile(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db:Session=Depends(get_database)
):
    try:
        user = extractUserByVerifyCredential(credentials,db)
        if user is None:
            raise HTTPException(status_code=404, detail="用户不存在")

        userInfo = getUserInfo(user)
        response = {
            "data":{
                "userInfo": userInfo
            }
        }
        return response
    except HTTPException:
        raise
    except Exception as e:
        userInfoLogger.error( f"[getUserProfile] 获取用户信息时发生未知错误 - {str( e )}" )
        raise HTTPException(status_code=500, detail=f"获取用户信息时发生未知错误 - {str(e)}")


class UserInfo(BaseModel):
    avatar: str
    nickname: str
    gender: str
    hobby: str

# 修改用户信息接口
@user_router.put('/users/me')
async def updateUserInfo(
    user_info: UserInfo,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db:Session=Depends(get_database)
):
    try:
        user = extractUserByVerifyCredential(credentials,db)
        if user is None:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        update_info = {}
        if user_info.avatar:
            update_info['avatar'] = user_info.avatar
        if user_info.nickname:
            update_info['nickname'] = user_info.nickname
        if user_info.gender:
            update_info['gender'] = user_info.gender
        if user_info.hobby:
            update_info['hobby'] = user_info.hobby

        if update_info:
            db.query(User).filter(User.id==user.id).update(update_info)
            db.commit()
        return JSONResponse(status_code=200, content={"message": "保存成功"})
    except ValidationError as e:
        return JSONResponse(status_code=422, content={"detail": str(e)})
    
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"message": f"保存失败: {str(e)}"})
    finally:
        db.close()






