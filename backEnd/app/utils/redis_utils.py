# redis_utils.py
import os
import redis
from dotenv import load_dotenv
from redis.exceptions import RedisError, ConnectionError
from backEnd.app.utils.logger import setup_logger

# 创建 Redis 连接日志
redis_connection_logger = setup_logger('redis-connection', fileName='redis-connection.log')

# 加载.env文件
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOTENV_PATH = os.path.join(ROOT_DIR, ".env")
if not os.path.exists(DOTENV_PATH):
    error_msg = f"无法找到 .env 文件"
    redis_connection_logger.warning(error_msg)
else:
    redis_connection_logger.warning("加载.env文件成功")
    load_dotenv(DOTENV_PATH)

class RedisManager:
    """ Redis连接管理类，使用连接池管理Redis连接 """
    _instance = None
    _initialized = False
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._redis_pool = None
            self._redis_client = None
            self._connect()
            self._initialized = True

    def _connect(self):
        """ 创建Redis连接池和客户端 """
        try:
            redis_host = os.getenv('REDIS_HOST','localhost')
            redis_port = int(os.getenv('REDIS_PORT',6379))
            redis_db = int(os.getenv('REDIS_DB',0))
            redis_password = os.getenv('REDIS_PASSWORD',None)

            if not isinstance(redis_host, str) or not redis_host.strip():
                error_msg = "REDIS_HOST 必须是一个非空字符串。"
                redis_connection_logger.error(error_msg)
                raise ValueError(error_msg)

            if not isinstance(redis_port, int) or not (0 < redis_port <= 65535):
                error_msg = "REDIS_PORT 必须是一个介于 1 和 65535 之间的整数。"
                redis_connection_logger.error(error_msg)
                raise ValueError(error_msg)

            if not isinstance(redis_db, int) or not (0 <= redis_db <= 15):  # Redis 默认最大 DB 是 15
                error_msg = "REDIS_DB 必须是一个介于 0 和 15 之间的整数。"
                redis_connection_logger.error(error_msg)
                raise ValueError(error_msg)

            self._redis_pool = redis.ConnectionPool(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                socket_timeout=5,
                socket_connect_timeout=5,
                decode_responses=True,
                max_connections=50
            )

            self._redis_client = redis.Redis(connection_pool=self._redis_pool)

            self._redis_client.ping()
            redis_connection_logger.info("成功连接到Redis")

        except ConnectionError as ce:
            error_msg = f"无法连接到Redis - {str(ce)}"
            redis_connection_logger.error(error_msg)
            raise RedisError(error_msg)
        except TimeoutError as te:
            error_msg = f"Redis连接超时 - {str(te)}"
            redis_connection_logger.error(error_msg)
            raise RedisError(error_msg)
        except ValueError as ve:
            error_msg = f"Redis配置参数错误 - {str(ve)}"
            redis_connection_logger.error(error_msg)
            raise RedisError(error_msg)
        except Exception as e:
            error_msg = f"Redis连接发生位置错误 - {str(e)}"
            redis_connection_logger.error(error_msg)
            raise RedisError(error_msg)

    def get_redis_client(self):
        """ 获取Redis客户端 """
        if self._redis_client is None:
            self._connect()
        return self._redis_client

    def get(self, key):
        """ 获取指定key的值 """
        try:
            client = self.get_redis_client()
            return client.get(key)
        except RedisError as re:
            error_msg = f"Redis获取key值发生错误 - {str(re)}"
            redis_connection_logger.error(error_msg)
            raise RedisError(error_msg)
        except Exception as e:
            error_msg = f"Redis获取key值发生未知错误 - {str(e)}"
            redis_connection_logger.error(error_msg)
            raise RedisError(error_msg)

    def delete(self,key):
        """ 删除指定key """
        try:
            client = self.get_redis_client()
            return client.delete(key)
        except RedisError as re:
            error_msg = f"Redis删除key发生错误 - {str(re)}"
            redis_connection_logger.error(error_msg)
            raise RedisError(error_msg)
        except Exception as e:
            error_msg = f"Redis删除key发生未知错误 - {str(e)}"
            redis_connection_logger.error(error_msg)
            raise RedisError(error_msg)

    def exists(self,key):
        """ 判断key是否存在 """
        try:
            client = self.get_redis_client()
            return client.exists(key)
        except RedisError as re:
            error_msg = f"Redis判断key是否存在发生错误 - {str(re)}"
            redis_connection_logger.error(error_msg)
            raise RedisError(error_msg)
        except Exception as e:
            error_msg = f"Redis判断key是否存在发生未知错误 - {str(e)}"
            redis_connection_logger.error(error_msg)
            raise RedisError(error_msg)

    def set(self,key,value,expire=None):
        """ 设置key-value """
        try:
            client = self.get_redis_client()
            return client.set(key,value,expire)
        except RedisError as re:
            error_msg = f"Redis设置key-value发生错误 - {str(re)}"
            redis_connection_logger.error(error_msg)
            raise RedisError(error_msg)
        except Exception as e:
            error_msg = f"Redis设置key-value发生未知错误 - {str(e)}"
            redis_connection_logger.error(error_msg)
            raise RedisError(error_msg)

def get_key_from_redis( name: str ):
    """ 从Redis中获取相关密钥 """
    if not isinstance( name, str ) or not name.strip():
        error_msg = "redis_key不为非空字符串"
        redis_connection_logger.error(error_msg)
        raise ValueError(error_msg)
    try:
        redis_manager = RedisManager()
        value = redis_manager.get(name)
        if not isinstance(value, str) or not value.strip():
            error_msg = f"从 Redis 获取的密钥无效或为空!"
            redis_connection_logger.error(error_msg)
            raise RedisError(error_msg)
        redis_connection_logger.info(f"成功从Redis获取密钥!")
        return value
    except RedisError as re:
        error_msg = f"从Redis获取密钥时发生错误: {re}"
        redis_connection_logger.error(error_msg)
        raise RedisError(error_msg)
    except Exception as e:
        error_msg = f"获取密钥时发生未知错误: {e}"
        redis_connection_logger.error(error_msg)
        raise RedisError(error_msg)

if __name__ == "__main__":
    print("开始测试Redis连接...")
    try:
        # 测试获取密钥函数
        print("1. 测试get_key_from_redis函数...")
        try:
            # 尝试获取一个不存在的键，应该抛出异常
            secret_key = get_key_from_redis("JWT_SECRET_KEY")
            print(f"获取密钥成功: {secret_key}")
        except RedisError as e:
            print(f"获取不存在的键时正确抛出异常: {e}")

        # 测试RedisManager类
        print("\n2. 测试RedisManager类...")
        redis_manager = RedisManager()

        # 测试设置和获取键值
        test_key = "WECHAT_SECRET_KEY"
        test_value = "8ca4524d10d633e14e34ba449b0e0ef0"

        print(f"设置键值对: {test_key} = {test_value}")
        redis_manager.set(test_key, test_value)

        retrieved_value = redis_manager.get(test_key)
        print(f"获取到的值: {retrieved_value}")

        if retrieved_value == test_value:
            print("设置和获取操作成功")
        else:
            print("设置和获取操作失败")

        # 测试键存在性检查
        exists = redis_manager.exists(test_key)
        print(f"键 {test_key} 是否存在: {exists}")
        #
        # # 测试删除操作
        # print(f"删除键: {test_key}")
        # redis_manager.delete(test_key)
        #
        # exists_after_delete = redis_manager.exists(test_key)
        # print(f"删除后键 {test_key} 是否存在: {exists_after_delete}")
        #
        # if not exists_after_delete:
        #     print("删除操作成功")
        # else:
        #     print("删除操作失败")

        # 测试单例模式
        print("\n3. 测试单例模式...")
        redis_manager2 = RedisManager()
        if redis_manager is redis_manager2:
            print("单例模式工作正常")
        else:
            print("单例模式异常")

        print("\n所有测试完成!")

    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

