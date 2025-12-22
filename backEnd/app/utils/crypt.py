import re
import os
import base64
import binascii
import redis
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

# Redis连接配置 Redis版本:3.2.100
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 1,
    'password': None,
    'decode_responses': False
}

# 获取Redis连接
def get_redis_connection():
    try:
        r = redis.Redis(**REDIS_CONFIG) 
        r.ping()  # 测试连接是否成功
        return r
    except Exception as e:
        raise ConnectionError(f"Redis 连接失败: {e}")

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
        raise ValueError(f"base64解码失败: {str(e)}")

def safe_b64encode(data:bytes)->str:
    return base64.b64encode(data).decode('utf-8')
    
# 从Redis获取主密钥(如没有则创建并存储到Redis中)
def get_master_key():
    try:
        redis_client = get_redis_connection()
        
        master_key_b64 = redis_client.get('MASTER_KEY')
        if not master_key_b64:
            new_master_key = os.urandom(32)
            master_key_b64 = safe_b64encode(new_master_key)
            redis_client.set('MASTER_KEY',master_key_b64)
            return new_master_key
        
        if isinstance(master_key_b64,bytes):
            master_key_b64 = master_key_b64.decode('utf-8')
            
        return safe_b64decode(master_key_b64.strip())
    except Exception as e:
        return os.urandom(32)
    
def encrypt_sec_key(sec_key:bytes,master_key:bytes):
    try:
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(master_key),modes.CBC(iv),backend=default_backend())
        encryptor = cipher.encryptor()
    
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_key = padder.update(sec_key)+padder.finalize()
        encrypted_key = encryptor.update(padded_key)+encryptor.finalize()

        combined = iv + encrypted_key
        return base64.b64encode(combined).decode('utf-8')
    except Exception as e:
        raise ValueError(f"加密SEC_KEY失败: {str(e)}")

def decrypt_sec_key(encrypted_sec_key_b64:str,master_key:bytes):
    try:
        combined = safe_b64decode(encrypted_sec_key_b64)

        if len(combined) < 16:
            raise ValueError("加密数据太短")
        iv = combined[:16]
        encrypted_key = combined[16:]

        cipher = Cipher(algorithms.AES(master_key),modes.CBC(iv),backend=default_backend())
        decryptor = cipher.decryptor()

        decrypted_padded = decryptor.update(encrypted_key)+decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        sec_key = unpadder.update(decrypted_padded)+unpadder.finalize()

        if len(sec_key) != 32:
            raise ValueError(f"解密的sec_key长度不正确: {len(sec_key)}字节，应为32字节")
        return sec_key
    except Exception as e:
        raise ValueError(f"解密sec_key失败: {str(e)}")

def get_sec_key() -> bytes:
    try:
        master_key = get_master_key()
        redis_client = get_redis_connection()
        if redis_client:
            encrypt_sec_key_b64 = redis_client.get('SEC_KEY')
            if encrypt_sec_key_b64:
                try:
                    if isinstance(encrypt_sec_key_b64,bytes):
                        encrypt_sec_key_b64 = encrypt_sec_key_b64.decode('utf-8')
                    sec_key = decrypt_sec_key(encrypt_sec_key_b64,master_key)
                    return sec_key
                except ValueError as e:
                    pass
                except Exception as e:
                    pass

        new_sec_key = os.urandom(32)
        if redis_client:
            try:
                encrypt_sec_key_b64 = encrypt_sec_key(new_sec_key,master_key)
                redis_client.set('SEC_KEY',encrypt_sec_key_b64)
            except Exception as e:
                pass
        return new_sec_key
    except Exception as e:
        return os.urandom(32)

def encrypt(data:str)->str:
    if not data:
        raise ValueError("加密数据不能为空")
    try:
        sec_key = get_sec_key()
        if len(sec_key) != 32:
            raise ValueError(f"sec_key长度不正确: {len(sec_key)}字节，应为32字节")
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
        raise ValueError(f"加密失败: {str(e)}")


def decrypt(encrypted_date_base64: str) -> str:
    if not encrypted_date_base64:
        raise ValueError("密文不能为空")

    try:
        sec_key = get_sec_key()
        if len(sec_key) != 32:
            raise ValueError(f"sec_key长度不正确: {len(sec_key)}字节，应为32字节")

        combined_data = base64.b64decode(encrypted_date_base64).decode('utf-8')

        parts = combined_data.split('_')
        if len(parts) != 2:
            raise ValueError("密文格式错误：缺少分隔符")
        iv_base64, encrypted_date_base64 = parts

        iv = safe_b64decode(iv_base64)
        ciphertext = safe_b64decode(encrypted_date_base64)
        if len(iv) != 16:
            raise ValueError(f"IV长度不正确: {len(iv)}字节，应为16字节")

        cipher = Cipher(algorithms.AES(sec_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()
        return decrypted_data.decode('utf-8')
    except Exception as e:
        raise ValueError(f"解密失败: {str(e)}")


def get_encryption_info():
    """获取加密配置信息"""
    try:
        master_key = get_master_key()
        sec_key = get_sec_key()

        return {
            "algorithm": "AES-256-CBC",
            "master_key_length": len(master_key),
            "sec_key_length": len(sec_key),
            "key_valid": len(master_key) == 32 and len(sec_key) == 32
        }
    except Exception as e:
        return {
            "algorithm": "AES-256-CBC",
            "error": str(e)
        }

# if __name__ == '__main__':
#     openid = "ojr2g7T_6rL88u-HEllD8Xs--860"
#     encrypted_data = encrypt(openid)
#     print(encrypted_data)
#     decrypted_data = decrypt(encrypted_data)
#     print(decrypted_data)
#     print(get_encryption_info())



                