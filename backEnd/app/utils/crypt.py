import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


def encrypt(data:str,key:bytes,iv: bytes)-> bytes:
    # 将字符串转换为字节
    data_bytes = data.encode('utf-8')
    # 使用 AES-256 加密模式进行加密
    cipher = Cipher(algorithms.AES(key),modes.CBC(iv),backend=default_backend)
    encryptor = cipher.encryptor()
    # 填充数据，使其成为 16 字节的倍数
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data_bytes)+padder.finalize()
    #执行加密
    ciphertext = encryptor.update(padded_data)+encryptor.finalize()
    #转化为base64字符串
    encrypted_data = base64.b64encode(ciphertext).decode('utf-8')
    return encrypted_data

def decrypt(ciphertext_base64:bytes,key:bytes,iv:bytes) -> str :
    # 将 Base64 字符串解码为字节数据
    ciphertext = base64.b64decode(ciphertext_base64)
    # 使用相同的密钥和 IV 解密
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    # 创建解密器并解密数据
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
    # 去除填充
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()
    # 返回解密后的字符串
    return decrypted_data.decode('utf-8')

#test
""" if __name__ == "__main__" :
    key = os.urandom(32)
    iv = os.urandom(16)
    
    data = "token-ojr2g7T_6rL88u-HEllD8Xs--860-1740058629"
    ciphertext = encrypt(data,key,iv)
    print(f"encrypted data:{ciphertext}")
    decrypted_data = decrypt(ciphertext,key,iv)
    print(f"decrypted data:{decrypted_data}") """
