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

from backEnd.app.utils.encryption import get_jwt_secret_key
from backEnd.app.utils.logger import setupLogger
from backEnd.app.utils.redis_utils import RedisManager

jwt_handler_logger = setupLogger( "jwt_handler" , "jwt_handler.log" )
TZ = pytz.timezone('Asia/Shanghai')
redis_manager_for_jwt_operations = RedisManager()

# JWT配置
ALGORITHM = os.getenv('ALGORITHM')
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

def createBasePayload( expire_delta:timedelta=None ) -> dict:
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

def createUserToken( data:dict , expires_delta:timedelta=None ) -> str:
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
        base_payload = createBasePayload( expires_delta )
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

def isValidJwtStructure(token: str) -> bool:
    """ 校验 token 是否符合 JWT 的基本结构。"""
    if not token or not isinstance(token, str):
        jwt_handler_logger.error("[isValidJwtStructure] token 为空或非字符串")
        return False

    try:
        token_parts = token.split(".")
        if len(token_parts) != 3:
            jwt_handler_logger.error("[isValidJwtStructure] token 不是标准的三段式 JWT")
            return False
        base64url_pattern = r'^[A-Za-z0-9_-]*$'
        for part in token_parts:
            if not part or not re.match(base64url_pattern, part):
                jwt_handler_logger.error("[isValidJwtStructure] token 部分不符合 Base64Url 编码规则")
                return False
        header = jwt.get_unverified_header(token)
        if not header or header.get("alg") != ALGORITHM or header.get("typ") != "JWT":
            jwt_handler_logger.error("[isValidJwtStructure] token 签名算法或类型无效")
            return False

        return True
    except Exception as e:
        jwt_handler_logger.error(f"[isValidJwtStructure] 校验 token 结构时发生错误: {str(e)}")
        return False

def decodeJwtPayload(token: str) -> Optional[Dict[str, Any]]:
    """ 从token中解析出payload """
    if not isValidJwtStructure(token):
        return None

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        jwt_handler_logger.info("[decodeJwtPayload] 成功解析 payload")
        return payload
    except jwt.InvalidTokenError:
        jwt_handler_logger.error("[decodeJwtPayload] token 签名无效")
        return None
    except Exception as e:
        jwt_handler_logger.error(f"[decodeJwtPayload] 解析 payload 时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"解析 payload 时发生错误: {str(e)}")

def validatePayloadFields(payload: Dict[str, Any], required_fields: List[str]) -> bool:
    """ 校验 payload 中的字段是否满足要求 """
    for field in required_fields:
        if field not in payload:
            jwt_handler_logger.error(f"[validatePayloadFields] payload 缺少必要字段: {field}")
            return False
    exp = payload.get("exp")
    if exp and datetime.now(TZ).timestamp() >= exp:
        jwt_handler_logger.warning("[validatePayloadFields] token 已过期")
        return False
    iat = payload.get("iat")
    if iat and datetime.now(TZ).timestamp() < iat:
        jwt_handler_logger.warning("[validatePayloadFields] token 未到生效时间")
        return False
    nbf = payload.get("nbf")
    if nbf and datetime.now(TZ).timestamp() < nbf:
        jwt_handler_logger.warning("[validatePayloadFields] token 未到生效时间")
        return False
    jti = payload.get("jti")
    if jti and (not isinstance(jti, str) or not jti.strip()):
        jwt_handler_logger.error("[validatePayloadFields] jti 字段无效")
        return False
    sub = payload.get("sub")
    if not sub or not isinstance(sub, str) or not sub.strip():
        jwt_handler_logger.error("[validatePayloadFields] sub 字段无效")
        return False
    jwt_handler_logger.info("[validatePayloadFields] payload 字段校验通过")
    return True

def verifyTokenFormatAndGetPayload( token: str , required_fields: List[str ] ) -> Optional[Dict[str, Any ] ]:
    """ 验证token，并返回解析后的payload """
    # 检查 token 是否在黑名单中
    try:
        if redis_manager_for_jwt_operations.exists(f"jwt_blacklist:{token}"):
            jwt_handler_logger.warning("[verifyTokenFormatAndGetPayload] token 在黑名单中")
            return None
    except Exception as e:
        jwt_handler_logger.error(f"[verifyTokenFormatAndGetPayload] 检查黑名单时发生错误: {str(e)}")
        return None

    # 解析 payload
    payload = decodeJwtPayload(token)
    if not payload:
        return None

    # 校验 payload 字段
    if not validatePayloadFields(payload, required_fields):
        return None

    jwt_handler_logger.info("[verifyTokenFormatAndGetPayload] token 验证通过")
    return payload

