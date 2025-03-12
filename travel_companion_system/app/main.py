from sqlalchemy.exc import SQLAlchemyError
from app.database import get_database
from sqlalchemy.orm import Session
from app.utils.crypt import encrypt, decrypt
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import uvicorn
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


# 测试数据库连接接口
@app.get("/test_db")
def test_db(db: Session = Depends(get_database)):
    try:
        result = db.excute("SELECT 1")
        return {"result": result.scalar()}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'SQL error: {str(e)}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Unexpected Error: {str(e)}')


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
