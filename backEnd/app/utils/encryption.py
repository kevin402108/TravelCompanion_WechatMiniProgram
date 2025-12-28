import re
import os
import base64
import binascii
import redis
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from dotenv import load_dotenv

from backEnd.app.utils.redis_utils import get_key_from_redis , RedisManager
from backEnd.app.utils.logger import setup_logger

# 日志记录器
encryption_logger = setup_logger( 'crypt_logger' , 'crypt_logger.log' )

# 加载.env文件
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOTENV_PATH = os.path.join(ROOT_DIR, ".env")
if not os.path.exists(DOTENV_PATH):
    error_msg = f"无法找到 .env 文件"
    encryption_logger.warning( error_msg )
else:
    encryption_logger.warning( "加载.env文件成功" )
    load_dotenv(DOTENV_PATH)

# redis管理器
redis_manager_for_encryption = None
try:
    redis_manager_for_encryption = RedisManager()
except Exception as e:
    encryption_logger.error(f"无法初始化Redis管理器 - {e}")


def get_key(key_name: str,redis_manager: RedisManager = None):
    """ 专门获取各种密钥，非密钥不要用此函数 """
    try:
        # 优先从Redis获取key
        try:
            value = get_key_from_redis(key_name)
            if value:
                encryption_logger.info(f"成功从Redis获取key: {key_name}")
                return value
        except Exception as e:
            encryption_logger.warning(f"从Redis获取key{key_name}时发生错误: {e}")

        # 如果无法从Redis获取，尝试从本地获取
        local_value = os.getenv(key_name)
        if local_value:
            encryption_logger.info(f"成功从本地获取key:{key_name}")
            try:
                redis_manager_for_encryption.set(key_name, local_value)
                encryption_logger.info(f"成功将本地key{key_name}保存到Redis")
            except Exception as e:
                encryption_logger.warning(f"保存本地key{key_name}到Redis失败: {e}")
            return local_value
    except Exception as e:
        encryption_logger.error(f"无法获取key {key_name}: {e}")
        return None

# Base64解码(安全版)
def safe_b64decode(data:str) -> bytes:
    if not data:
        raise ValueError("Base64数据为空")

    data = data.strip()
    padding_needed = 4 - len(data) % 4
    if padding_needed != 4:
        data += '=' * padding_needed
    try:
        return base64.b64decode(data,validate=True)
    except binascii.Error as e:
        data = re.sub(r'[^A-Za-z0-9+/=]', '', data)
        padding_needed = 4 - len(data) % 4
        if padding_needed != 4:
            data += '=' * padding_needed
        return base64.b64decode(data,validate=True)
    except Exception as e:
        raise ValueError(f"base64解码失败: {e}")

def safe_b64encode(data:bytes)->str:
    return base64.b64encode(data).decode('utf-8')

def get_crypt_sec_key():
    """ 获取32字节的安全密钥，优先从Redis获取，失败时尝试本地获取，没有返回异常 """
    try:
        sec_key_b64 = get_key("CRYPT_SEC_KEY")
        if sec_key_b64:
            try:
                sec_key = safe_b64decode(sec_key_b64)
                if len(sec_key) == 32:
                    encryption_logger.info( f"成功获取密钥" )
                    return sec_key
            except ValueError as ve:
                encryption_logger.warning( f"解码安全密钥失败: {ve}" )
            except Exception as e:
                encryption_logger.error( f"处理安全密钥时发生错误: {e}" )
        return None
    except Exception as e:
        encryption_logger.error( f"获取密钥时发生错误: {e}" )
        return None

def encrypt(data:str)->str:
    if not data:
        raise ValueError("加密数据不能为空")
    try:
        sec_key = get_crypt_sec_key()
        if not sec_key or len(sec_key) != 32:
            raise ValueError(f"密钥为空或密钥长度不正确！")
        iv = os.urandom(16)
        data_bytes = data.encode('utf-8')

        cipher = Cipher(algorithms.AES(sec_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data_bytes)+padder.finalize()
        ciphertext = encryptor.update(padded_data)+encryptor.finalize()

        iv_base64 = base64.b64encode(iv).decode('utf-8')
        ciphertext_base64 = base64.b64encode(ciphertext).decode('utf-8')
        combined_data = f"{iv_base64}_{ciphertext_base64}"

        combined_data_b64 = base64.b64encode(combined_data.encode('utf-8')).decode('utf-8')
        return combined_data_b64
    except Exception as e:
        raise ValueError(f"加密失败: {e}")


def decrypt(encrypted_data_base64: str) -> str:
    if not encrypted_data_base64:
        raise ValueError("密文不能为空")
    try:
        sec_key = get_crypt_sec_key()
        if not sec_key or len(sec_key) != 32:
            raise ValueError(f"密钥为空或密钥长度不正确！")

        combined_data = base64.b64decode(encrypted_data_base64).decode('utf-8')
        parts = combined_data.split('_')
        if len(parts) != 2:
            raise ValueError("密文格式错误！")
        iv_base64, encrypted_data_base64 = parts

        iv = safe_b64decode(iv_base64)
        ciphertext = safe_b64decode(encrypted_data_base64)
        if len(iv) != 16:
            raise ValueError(f"IV长度不正确: {len(iv)}字节，应为16字节")

        cipher = Cipher(algorithms.AES(sec_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()
        return decrypted_data.decode('utf-8')
    except Exception as e:
        raise ValueError(f"解密失败: {e}")

def get_jwt_secret_key():
    """ 获取 JWT_SECRET_KEY，优先从 Redis 获取，如果获取不到，则从 .env 文件中获取。"""
    try:
        jwt_secret_key = get_key("JWT_SECRET_KEY")
        if jwt_secret_key:
            encryption_logger.info( f"成功获取密钥" )
            return jwt_secret_key
        return None
    except Exception as e:
        encryption_logger.error( f"获取密钥时发生错误: {e}" )
        return None

# if __name__ == '__main__':
#     str1 = "abcdefg"
#     encrypted_data = encrypt(str1)
#     print(encrypted_data)
#     decrypted_data = decrypt(encrypted_data)
#     print(decrypted_data)
#     print(get_jwt_secret_key())



                