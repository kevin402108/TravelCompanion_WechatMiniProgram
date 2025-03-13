from fastapi.encoders import jsonable_encoder
from sqlalchemy import text
import uvicorn
from app.database import get_database, engine, test_connection
from sqlalchemy.orm import Session
from app.utils.crypt import encrypt, decrypt
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import inspect
import requests
import time
import os

app = FastAPI()

class LoginRequest(BaseModel):
    code: str


# 登录接口 POST请求
@app.post('/auth/login/')
def login(loginCode: LoginRequest):
    url = f"https://api.weixin.qq.com/sns/jscode2session?appid=wxa35b788e7a7760be&secret=2747dff5884689877ecd3ebe4f923508&js_code={loginCode.code}&grant_type=authorization_code"
    result = requests.get(url)
    data = result.json()
    openid = data["openid"]
    session_key = data["session_key"]

    iat = time.time()  # iat token创建时间
    token = f"token-{openid}-{int(iat)}"
    key = os.urandom(32)
    iv = os.urandom(16)
    encrypted_token = encrypt(token, key, iv)  # 将加密的token后转化base64字符串
    response = {
        "data": {
            "token": encrypted_token,
            "loginStatus": 1  # 登录态 1:已登录 0:未登录
        }
    }
    return response


# 启动时测试数据库连接
test_connection()


# 测试能否手动连接数据库
@app.get("/ping_db")
def ping_db(db: Session = Depends(get_database)):
    try:
        result = db.execute(text("SHOW TABLES"))
        # 将查询结果转换为字典列表
        tables = [dict(row._mapping) for row in result]
        return jsonable_encoder({"result": tables, "status": "数据库连接成功"})
    except Exception as  e:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {e}")


@app.get("/")
def welcome():
    return {"messgae":"Welcome to @KevinChan's Page!"}

for route in app.routes:
    print(route.path)
