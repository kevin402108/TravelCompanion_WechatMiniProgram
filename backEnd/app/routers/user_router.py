from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backEnd.app.utils.logger import setup_logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, ProgrammingError, DataError, IntegrityError
from fastapi import APIRouter, Depends, HTTPException
from backEnd.app.database import get_database
from backEnd.app.models import User

# 设置路由
user_router = APIRouter()
# 设置日志记录器
logger = setup_logger('user_info_logger')
def get_user_info(user):
    """ 获取用户基本信息 """
    return {
        "id": user.id,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "gender": user.gender,
        "hobby": user.hobby
    }
    

@user_router.get('/user/profile')
def get_user(
    id:int,
    db=Depends(get_database)
):
    try:
        #从数据库中获取对应id的用户信息
        user = db.query(User).filter(User.id == id).first()
        if user:
            # 用户信息
            userInfo = get_user_info(user)
            response = {
                "data":{
                    "userInfo":userInfo
                }
            }
            logger.info(f"获取用户信息成功 , 用户ID: {id}")
            return response
        else:
            #未找到用户，抛出未找到对应用户异常
            raise HTTPException(status_code=404, detail=f"无法查询到id为{id}的用户!")
    except HTTPException:
        raise
    except OperationalError as e:
            # 数据库操作异常，抛出数据库操作异常
            logger.error(f"数据库连接错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"数据库连接错误: {str(e)}")
    except ProgrammingError as e:
        # 处理 SQL 语句执行异常
        logger.error(f"SQL 执行错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SQL 执行错误: {str(e)}")
    except DataError as e:
        # 处理数据类型不匹配异常
        logger.error(f"数据类型不匹配错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"数据类型不匹配错误: {str(e)}")
    except IntegrityError as e:
        # 处理完整性约束异常
        logger.error(f"完整性约束违反错误: {str(e)}")
        raise HTTPException(status_code=409, detail=f"完整性约束违反错误: {str(e)}")
    except Exception as e:
        # 处理其他未知异常
        logger.error(f"未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"未知错误: {str(e)}")


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