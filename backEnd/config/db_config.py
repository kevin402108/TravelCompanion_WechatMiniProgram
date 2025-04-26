import os
from dotenv import load_dotenv

# 当前项目所处环境
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
if ENVIRONMENT == "development":
    # print("当前处于开发环境")
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(env_path)

DB_USER = os.getenv("DB_USER")
DB_PWD = os.getenv("DB_PWD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


# print(DB_USER, DB_PWD, DB_HOST, DB_PORT, DB_NAME)
if not all([DB_USER, DB_PWD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError("缺失部分或全部数据库环境变量，请检查后重试！")

# 数据库url
DB_URL = f'mysql+pymysql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
# print(DB_URL)

# 生产环境连接配置
if ENVIRONMENT == "production":
    DB_CONFIG = {
        "echo": False,
        "pool_size": 50,
        "max_overflow": 100,
        "pool_recycle": 3600,
        "pool_timeout": 30,
        "pool_pre_ping": True,
        "pool_use_lifo": True,
        "isolation_level": "REPEATABLE READ",
        "connect_args": {"charset": "utf8mb4"},
    }

# 开发环境连接配置
elif ENVIRONMENT == "development":
    DB_CONFIG = {
        "echo": True,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 1800,
        "pool_timeout": 15,
        "pool_pre_ping": True,
        "pool_use_lifo": True,
        "isolation_level": "REPEATABLE READ",
        "connect_args": {"charset": "utf8mb4"},
    }
