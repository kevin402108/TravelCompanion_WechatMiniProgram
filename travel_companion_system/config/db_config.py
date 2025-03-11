import os
from dotenv import load_dotenv

#当前项目所处环境
ENVIRONMENT = os.getenv("ENVIRONMENT","production")
if ENVIRONMENT == "development":
    # print("当前处于开发环境")
    env_path = os.path.join(os.path.dirname(__file__),".env")
    load_dotenv(env_path)

DB_USER = os.getenv("DB_USER")
DB_PWD = os.getenv("DB_PWD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

print(DB_USER,DB_PWD,DB_HOST,DB_PORT,DB_NAME)
if not all([DB_USER,DB_PWD,DB_HOST,DB_PORT,DB_NAME]):
    print("ERROR!")
    raise ValueError("缺失部分或全部数据库环境变量，请检查后重试！")
