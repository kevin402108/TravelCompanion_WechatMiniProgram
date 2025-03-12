from config.db_config import DB_URL, DB_CONFIG
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
    finally:
        db.close()


# 测试数据库连接
def test_db_connect() -> bool:
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT * FROM USER")
            print(result.fetchone())
        return True
    except Exception as e:
        print(e)
        return False


print(test_db_connect())
