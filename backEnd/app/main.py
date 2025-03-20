import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from fastapi import FastAPI
# from backEnd.app.database import test_connection
# from backEnd.app.routers.db_router import db_router
from backEnd.app.routers.login_router import login_router

app = FastAPI()
# app.include_router(db_router)
app.include_router(login_router)


@app.get("/")
def welcome():
    return {"message": "You're visting @Kevin-467's page!"}


# 启动时测试数据库连接
# try:
#     test_connection()
# except Exception as e:
#     print(f"数据库连接失败:{e}")

# for route in app.routes:
#     print(route.path)

