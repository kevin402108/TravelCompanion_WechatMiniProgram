import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker

# 读取 .env 文件(绝对路径)
dotenv_path = os.path.join(os.path.dirname(__file__),'..','config','.env')
#print(dotenv_path)
load_dotenv(dotenv_path=dotenv_path)
    
environment = os.getenv("ENVIRONMENT","production")
print(environment)


# 获取数据库信息
DB_USER = os.getenv("DB_USER")
DB_PWD = os.getenv("DB_PWD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

#数据库URL
DB_URL = f'mysql+asyncmy://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
# print(DB_URL)

if environment == "development":
    engine = create_async_engine(
        DB_URL, 
        echo=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800,
        pool_timeout=15,
        pool_per_ping=True,
        pool_use_lifo=True,
        isolation_level="REPEATABLE READ",
        connect_args={"charset": "utf8mb4"} 
    )
elif environment == "production":
    engine = create_async_engine(
        DB_URL, 
        echo=False,
        pool_size=50,
        max_overflow=100,
        pool_recycle=3600,
        pool_timeout=30,
        pool_per_ping=True,
        isolation_level="REPEATABLE READ",
        connect_args={"charset": "utf8mb4"} 
    )

AsyncSessionLocal = sessionmaker()



