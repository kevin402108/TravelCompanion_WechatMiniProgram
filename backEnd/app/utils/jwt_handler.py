import os
import re
import jwt
import uuid
import pytz
import redis
import hashlib
from fastapi import HTTPException
from datetime import timedelta , datetime
from typing import List , Optional , Dict , Any

from sqlalchemy.orm import Session

from backEnd.app.models import User
from backEnd.app.utils.encryption import get_jwt_secret_key , decrypt
from backEnd.app.utils.logger import setup_logger
from backEnd.app.utils.redis_utils import RedisManager

# 日志记录器
jwt_handler_logger = setup_logger("jwt_handler","jwt_handler.log")

# 时区配置
TZ = pytz.timezone('Asia/Shanghai')

# JWT配置
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 15))
try:
    JWT_SECRET_KEY = get_jwt_secret_key()
    jwt_handler_logger.info("成功从Redis和.env文件中获取JWT配置")
except redis.exceptions.RedisError as re:
    jwt_handler_logger.critical(f"无法从获取 SECRET_KEY: {str(re)}")
    raise RuntimeError(f"无法初始化JWT配置:{str(re)}")
except ValueError as ve:
    jwt_handler_logger.critical(f"配置参数解析错误: {str(ve)}")
    raise RuntimeError("无法初始化JWT配置:请检查配置参数。")
except Exception as e:
    jwt_handler_logger.critical(f"初始化 JWT 配置时发生未知错误: {str(e)}")
    raise RuntimeError("无法初始化JWT配置:请检查系统配置。")

# Redis管理器
redis_manager_for_jwt_operations = RedisManager()

def _create_base_payload(expire_delta:timedelta=None) -> dict:
    """ 生成 JWT Token payload中的公共部分 """
    if expire_delta:
        expire = datetime.now(TZ) + expire_delta
    else:
        expire = datetime.now(TZ) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "iat": datetime.now(TZ),
        "nbf": datetime.now(TZ),
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }

def _verify_token_format(token:str,required_fields:List[str]) -> Optional[Dict[str, Any]]:
    if not token or not isinstance(token, str):
        jwt_handler_logger.error("[_verify_token_format] token格式无效: 为空或非字符串")
        return None

    # 检查token是否为标准的 JWT 格式
    try:
        token_parts = token.split(".")
        if len(token_parts) != 3:
            jwt_handler_logger.error("[_verify_token_format] token格式无效: 非标准的JWT格式")
            return None

        base64url_pattern = r'^[A-Za-z0-9_-]*$'
        for part in token_parts:
            if not part or not isinstance(part, str) or not part.strip():
                jwt_handler_logger.error("[_verify_token_format] token格式无效: 非标准的JWT格式")
                return None
            if not re.match(base64url_pattern, part):
                jwt_handler_logger.error("[_verify_token_format] token格式无效: 非标准的JWT格式")
                return None
    except Exception as e:
        jwt_handler_logger.error("[_verify_token_format] token格式错误: 无法解析为三段式")
        return None

    # 检查token是否在黑名单中
    try:
        if redis_manager_for_jwt_operations.exists(f"jwt_blacklist:{token}"):
            jwt_handler_logger.warning("[_verify_token_format] token在黑名单中")
            return None
    except Exception as e:
            jwt_handler_logger.error(f"[_verify_token_format] 在redis检查jwt黑名单时发生错误 - {str(e)}")
            return None

    try:
        header = jwt.get_unverified_header(token)
        if not header or header.get("alg") != ALGORITHM or header.get("typ") != "JWT":
            jwt_handler_logger.error("[_verify_token_format] token签名无效")
            return None
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])

        for field in required_fields:
            if field not in payload:
                jwt_handler_logger.error(f"[_verify_token_format] token缺少必要字段: {field}")
                return None

        exp = payload.get("exp")
        if exp and datetime.now(TZ).timestamp() >= exp:
            jwt_handler_logger.warning("[_verify_token_format] token已过期")
            try:
                redis_manager_for_jwt_operations.set(f"jwt_blacklist:{token}", "expired", expire=86400)
            except Exception as e:
                jwt_handler_logger.error(f"[_verify_token_format] 将过期令牌加入黑名单失败 - {str(e)}")
            return None

        iat = payload.get("iat")
        if iat and datetime.now(TZ).timestamp() < iat:
            jwt_handler_logger.warning("[_verify_token_format] token未到生效时间")
            return None

        nbf = payload.get("nbf")
        if nbf and datetime.now(TZ).timestamp() < nbf:
            jwt_handler_logger.warning("[_verify_token_format] token未到生效时间")
            return None

        jti = payload.get("jti")
        if jti and not isinstance(jti, str) or not jti.strip():
            jwt_handler_logger.error("[_verify_token_format] token中jti字段无效")
            return None

        sub = payload.get("sub")
        if not sub or not isinstance(sub, str) or not sub.strip():
            jwt_handler_logger.error("[_verify_token_format] token中sub字段无效")
            return None

        jwt_handler_logger.info("[_verify_token_format] token格式格式验证成功")
        return payload
    except jwt.InvalidTokenError:
        jwt_handler_logger.error("[_verify_token_format] token签名无效")
        return None
    except Exception as e:
        jwt_handler_logger.error(f"[_verify_token_format] token格式验证过程中发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"token格式验证过程中发生错误: {str(e)}")

def create_user_token(data:dict,expires_delta:timedelta=None) -> str:
    """ 生成 JWT Token """
    if not isinstance(data, dict) or data is None:
        jwt_handler_logger.error("[create_user_token] data参数为None或参数类型不为dict")
        raise HTTPException(status_code=500, detail="data参数为None或参数类型不为dict")

    if expires_delta and not isinstance(expires_delta, timedelta):
        jwt_handler_logger.error("[create_user_token] expires_delta参数必须为None或timedelta类型")
        raise HTTPException(status_code=500, detail="参数不合法 - expires_delta参数必须为None或timedelta类型")

    openid = data.get("openid")
    user_id = data.get("user_id")
    if user_id is None or not isinstance(user_id, int) or user_id <= 0:
        jwt_handler_logger.error("[create_user_token] user_id参数必须为正整数")
        raise HTTPException(status_code=500, detail="参数不合法 - user_id参数必须为正整数")

    if not isinstance(openid, str) or not openid.strip():
        jwt_handler_logger.error("[create_user_token] openid参数必须为非空字符串")
        raise HTTPException(status_code=500, detail="参数不合法 - openid参数必须为非空字符串")

    try:
        # payload模板
        base_payload = _create_base_payload(expires_delta)

        # 处理openid
        processed_data = data.copy()
        openid_hash = hashlib.sha256(openid.encode()).hexdigest()
        processed_data["openid_hash"] = openid_hash
        processed_data["user_type"] = "wechat_user"
        processed_data["token_type"] = "user_access"
        processed_data["sub"] = str(user_id)
        del processed_data["openid"]

        payload = {**base_payload, **processed_data}
        encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY , algorithm=ALGORITHM)
        jwt_handler_logger.info(f"[create_user_token] 成功生成用户token")
        return encoded_jwt
    except Exception as e:
        jwt_handler_logger.error(f"[create_user_token] JWT Token 生成失败 - {str(e)}")
        raise HTTPException(status_code=500, detail=f"JWT Token 生成失败 - {str(e)}")

def verify_user_token(token:str) -> Optional[Dict[str, Any]]:
    if not isinstance(token, str) or not token.strip():
        jwt_handler_logger.error("[verify_user_token] token参数必须为非空字符串")
        raise HTTPException(status_code=500, detail="参数错误 - token参数必须为非空字符串")
    required_fields =  ["sub", "iat", "exp", "jti", "nbf","user_id","openid_hash", "user_type", "token_type"]
    return _verify_token_format(token, required_fields)

def validate_user_identity(token:str,db:Session) -> Dict[str, Any]:
    if not isinstance(token, str) or not token.strip():
        jwt_handler_logger.error("[validate_user_identity] token参数必须为非空字符串")
        raise HTTPException(status_code=500, detail="参数错误 - token参数必须为非空字符串")

    try:
        payload = verify_user_token(token)
        if not payload:
            return {"valid": False, "message": "token格式或签名无效"}
    except HTTPException:
        raise

    user_id_str = payload.get("user_id")
    openid_hash = payload.get("openid_hash")
    user_type = payload.get("user_type")

    if user_type != "wechat_user":
        jwt_handler_logger.error(f"[validate_user_identity] 令牌类型错误: 期望wechat_user，实际{user_type}")
        return {"valid": False, "message": "token无效"}

    try:
        user_id = int(user_id_str) if user_id_str else None
    except ValueError:
        jwt_handler_logger.error(f"[validate_user_identity] user_id字段无效!")
        return {"valid": False, "message": " user_id 格式无效"}

    if not user_id or user_id <= 0:
        jwt_handler_logger.error(f"[validate_user_identity] user_id 无效!")
        return {"valid": False, "message": "user_id无效"}

    if not openid_hash or not isinstance(openid_hash, str) or not openid_hash.strip():
        jwt_handler_logger.error(f"[validate_user_identity] openid_hash 无效!")
        return {"valid": False, "message":"openid_hash无效"}

    try:
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.openid:
                jwt_handler_logger.error(f"[validate_user_identity] 不存在该ID的用户或用户openid不存在")
                return {"valid": False, "error": "不存在该ID的用户或用户openid不存在"}
        except Exception as db_error:
            jwt_handler_logger.error(f"[validate_user_identity] 查询用户信息时发生错误: {str(db_error)}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"数据库查询过程中发生错误: {str(db_error)}")

        try:
            decrypted_openid = decrypt(user.openid)
            if not decrypted_openid:
                jwt_handler_logger.error(f"[validate_user_identity] 解密openid失败")
                return {"valid": False, "error": "解密 openid 失败"}
        except Exception as decrypt_error:
            jwt_handler_logger.error(f"[validate_user_identity] 解密 openid 失败: {str(decrypt_error)}")
            return {"valid": False, "error": "解密 openid 异常"}

        expected_openid_hash = hashlib.sha256(decrypted_openid.encode()).hexdigest()
        if openid_hash != expected_openid_hash:
            jwt_handler_logger.error(f"[validate_user_identity] 令牌中的openid_hash无效")
            return {"valid": False, "message": "令牌中的openid_hash无效"}

        jwt_handler_logger.info(f"[validate_user_identity] 令牌验证通过")
        return {
            "valid": True,
            "user_id": user_id,
            "openid": decrypted_openid,
             "message": "令牌验证通过"
        }
    except HTTPException:
        raise
    except Exception as e:
        jwt_handler_logger.error(f"[validate_user_identity] 验证过程中发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"验证过程中发生错误: {str(e)}")


def get_user_info_from_token(token:str) -> Optional[Dict[str, Any]]:
    if not token or not isinstance(token, str) or not token.strip():
        jwt_handler_logger.error("[get_user_info_from_token] token参数必须为非空字符串")
        raise HTTPException(status_code=500, detail="参数错误 - token参数必须为非空字符串")

    try:
        validation_result = validate_user_identity(token)
        if validation_result.get("valid"):
            user_id = validation_result.get("user_id")
            openid = validation_result.get("openid")
            if user_id and isinstance(user_id, int) and openid and isinstance(openid, str):
                return {
                    "user_id": user_id,
                    "openid": openid
                }
            jwt_handler_logger.info(f"[get_user_info_from_token] 从JWT获取用户信息不完整: 缺少用户信息")
            return None
        else:
            jwt_handler_logger.info(f"[get_user_info_from_token] 从JWT获取用户信息失败: {validation_result.get('message')}")
            return None
    except HTTPException:
        raise
    except Exception as error:
        jwt_handler_logger.error(f"[get_user_info_from_token] 从token获取用户信息时发生未知错误: {str(error)}")
        raise HTTPException(status_code=500, detail=f"从token获取用户信息时发生未知错误: {str(error)}")

# def create_admin_token(data:dict,expires_delta:timedelta=None) -> str:
#     pass
#
# def verify_admin_token(token:str) -> Optional[Dict[str, Any]]:
#     pass
#
# def validate_admin_identity(token:str) -> bool:
#     pass
#
# def get_admin_info_from_token(token:str) -> Optional[Dict[str, Any]]:
#     pass