from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backEnd.app.utils.jwt_handler import get_user_info_from_token
from backEnd.app.utils.logger import setup_logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, ProgrammingError, DataError, IntegrityError
from fastapi import APIRouter , Depends , HTTPException
from backEnd.app.database import get_database
from backEnd.app.models import User

# 设置路由
user_router = APIRouter()
# 设置日志记录器
user_info_logger = setup_logger( 'user_info' , fileName= 'user_info.log' )

def get_user_info(user):
    """ 获取用户基本信息 """
    if not user:
        user_info_logger.error("[get_user_info] 用户信息不存在")
        return None

    user_info_logger.info(f"[get_user_info] 获取用户信息成功")
    return {
        "nickname": user.nickname,
        "avatar": user.avatar,
        "gender": user.gender,
        "hobby": user.hobby
    }
    

@user_router.get('/user/profile')
def get_user_profile(
    token:str,
    db:Session=Depends(get_database)
):
    try:
        current_user = get_current_user(token, db)
        if not current_user:
            raise HTTPException(status_code=404, detail="用户不存在")

        userInfo = get_user_info(current_user)
        response = {
            "data":{
                "userInfo": userInfo
            }
        }
        return response
    except HTTPException:
        raise
    except Exception as e:
        user_info_logger.error(f"[get_user_profile] 获取用户信息时发生未知错误 - {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取用户信息时发生未知错误 - {str(e)}")


class UserInfo(BaseModel):
    id: int
    avatar: str
    nickname: str
    gender: str
    hobby: str

# 修改用户信息接口
@user_router.put('/auth/updateUserInfo')
async def update_user_info(
    user_info: UserInfo,
    db:Session=Depends(get_database)
):
    try:
        print("收到的用户信息：", user_info)
        user_id = user_info.id
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise exceptions.UserNotFoundError()
        
        update_info = {}
        if user_info.avatar:
            update_info['avatar'] = user_info.avatar
        if user_info.nickname:
            update_info['nickname'] = user_info.nickname
        if user_info.gender:
            update_info['gender'] = user_info.gender
        if user_info.hobby:
            update_info['hobby'] = user_info.hobby
        print("更新信息：", update_info)
        
        # 只有有更新内容时才执行更新操作
        if update_info:
            db.query(User).filter(User.id==user_id).update(update_info)
            db.commit()

        return JSONResponse(status_code=200, content={"message": "保存成功"})
    except ValidationError as e:
        return JSONResponse(status_code=422, content={"detail": e.errors()})
    
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"message": f"保存失败: {str(e)}"})
    finally:
        db.close()

#  从请求数据中的token获取当前用户信息
def get_current_user(token:str,db:Session=Depends(get_database)):
    if not token or not isinstance(token, str) or not token.strip():
        user_info_logger.error("[get_current_user] token无效 - token格式不符合要求")
        raise HTTPException(status_code=401, detail="token无效 - token格式不符合要求")
    try:
        user_info = get_user_info_from_token(token,db)
        user_info_logger.info(f"[get_current_user] 获取当前用户信息:{user_info}")
        if not user_info:
            user_info_logger.error("[get_current_user] token无效或已过期")
            raise HTTPException(status_code=401, detail="token无效或已过期")

        user_id = user_info.get("user_id")
        if not user_id or not isinstance(user_id, int) or user_id <= 0:
            user_info_logger.error("[get_current_user] 用户ID无效")
            raise HTTPException(status_code=401, detail="用户ID无效")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user_info_logger.error("[get_current_user] 用户不存在")
            raise HTTPException(status_code=404, detail="用户不存在")
        return user
    except HTTPException:
        raise
    except Exception as e:
        user_info_logger.error(f"[get_current_user] 获取当前用户信息时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取当前用户信息时发生未知错误: {str(e)}")

