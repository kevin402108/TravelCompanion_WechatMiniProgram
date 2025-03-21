import logging
import backEnd.app.utils.exceptions as exceptions
from sqlalchemy.exc import OperationalError, ProgrammingError, DataError, IntegrityError
from fastapi import APIRouter, Depends
from backEnd.app.database import get_database
from backEnd.app.models import User

user_router = APIRouter()

@user_router.get('/user/profile')
def get_user(id:int,token:str,db=Depends(get_database)):
    try:
        #从数据库中获取对应id的用户信息
        user = db.query(User).filter(User.id==id).first()
        if user:
            # 用户信息
            userInfo = {
                "id":user.id,
                "nickname":user.nickname,
                "avatar":user.avatar,
                "gender":user.gender,
                "hobby":user.hobby
            }
            response = {
                "data":userInfo
            }
            return response
        else:
            #未找到用户，抛出未找到对应用户异常
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
        # 处理其他未知异常
        raise exceptions.UnknownError(str(e))
    