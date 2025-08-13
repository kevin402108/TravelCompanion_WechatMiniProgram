from fastapi import APIRouter

from backEnd.config.db_config import DB_URL, DB_CONFIG
from sqlalchemy import create_engine,text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

router = APIRouter()
engine = create_engine(DB_URL, **DB_CONFIG)
sessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=True,
    future=True
)

Base = declarative_base()
Base.metadata.create_all(engine)

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

# 创建数据库表
def create_tables():
    Base.metadata.create_all(engine)

