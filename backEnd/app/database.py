from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from requests import Session

from backEnd.config.db_config import DB_URL, DB_CONFIG
from sqlalchemy import create_engine,text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

router = APIRouter()

# 创建同步数据库引擎
engine = create_engine(DB_URL, **DB_CONFIG)
print(engine)

# 创建同步会话类
sessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=True,
    future=True  # 启用SQLAlchemy 2.0的新特性
)

# 基类，用于声明模型
Base = declarative_base()

# 创建数据库连接
def get_database():
    db = sessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# 测试数据库连接
def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES"))
            print(result.fetchall())
        print("数据库连接成功！")
    except Exception as e:
        print(f"数据库连接失败：{e}")

