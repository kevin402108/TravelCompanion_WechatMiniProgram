import time
from functools import wraps

from sqlalchemy import create_engine , text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backEnd.app.utils.logger import setup_logger
from backEnd.config.db_config import DB_URL , DB_CONFIG

mysql_logger = setup_logger('mysql-connection', fileName='mysql-connection.log')
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

def retry_on_mysql_error(max_retries=3):
    """MySQL操作重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        mysql_logger.warning(f"MySQL操作失败，第{attempt + 1}次重试: {str(e)}")
                        time.sleep(0.5 * (attempt + 1))
                    else:
                        mysql_logger.error(f"MySQL操作在{max_retries}次重试后仍然失败: {str(e)}")
            raise last_exception
        return wrapper
    return decorator

def get_database():
    """获取数据库连接"""
    last_exception = None
    for attempt in range(3):
        try:
            db = sessionLocal()
            yield db
            break
        except Exception as e:
            last_exception = e
            if attempt < 2:
                mysql_logger.warning(f"数据库连接失败，第{attempt + 1}次重试: {str(e)}")
                time.sleep(0.5 * (attempt + 1))
            if 'db' in locals():
                db.close()
        finally:
            if 'db' in locals():
                db.close()
    if last_exception:
        raise last_exception



