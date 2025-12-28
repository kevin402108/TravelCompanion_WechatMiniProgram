import os




ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
DB_USER = os.getenv("DB_USER")
DB_PWD = os.getenv("DB_PWD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
if not all([DB_USER, DB_PWD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError("缺失部分或全部数据库环境变量，请检查后重试！")
DB_URL = f'mysql+pymysql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
SQLALCHEMY_ECHO = (ENVIRONMENT == "development")

# 基础连接配置
DB_CONFIG_BASE = {
    "pool_pre_ping": True,
    "pool_use_lifo": True,
    "isolation_level": "REPEATABLE READ",
    "connect_args": {"charset": "utf8mb4"},
}

# 不同环境特定连接配置
ENV_CONFIGS = {
    "production": {
        "echo": False,
        "pool_size": 50,
        "max_overflow": 100,
        "pool_recycle": 3600,
        "pool_timeout": 30
    },
    "development": {
        "echo": True,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 1800,
        "pool_timeout": 15
    }
}

ENV_SPEC_CONFIG = ENV_CONFIGS.get(ENVIRONMENT, ENV_CONFIGS["production"])
DB_CONFIG = {**DB_CONFIG_BASE, **ENV_SPEC_CONFIG}
