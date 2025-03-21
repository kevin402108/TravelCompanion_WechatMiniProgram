from fastapi import APIRouter
from pydantic import BaseModel

user_router = APIRouter()

class getUser(BaseModel):
    id:int
    token:str
@user_router.get('/user/{id}')
def get_user(userInfo:getUser):
    id = userInfo.id
    token = userInfo.token
    response = {
        "data": {
             "avatar":"头像", 
             "nickname":"kevinchan", 
             "gender":"男",  
             "hobby":"跑步"
        }
    }