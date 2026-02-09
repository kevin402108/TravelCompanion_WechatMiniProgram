import hashlib

from fastapi.params import Depends
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backEnd.app.database import get_database
from backEnd.app.utils.encryption import decrypt
from backEnd.app.utils.jwt_handler import verifyTokenFormatAndGetPayload
from backEnd.app.utils.logger import setupLogger
from backEnd.app.models import User

authLogger = setupLogger( "auth_utils" , fileName= "auth.log" )

def getTokenFromCredential(credentials: HTTPAuthorizationCredentials) -> str:
    """ 从 credentials 中安全提取 token。"""
    if credentials is None:
        authLogger.warning( "[getTokenFromCredential] credentials 为 None" )
        raise HTTPException(status_code=401, detail="提取token失败 - 未获取到用户凭证")
    if not isinstance(credentials, HTTPAuthorizationCredentials):
        authLogger.warning( f"[getTokenFromCredential] credentials 类型错误，期望的类型为 HTTPAuthorizationCredentials，实际为 {type( credentials ).__name__}" )
        raise TypeError("credentials参数类型错误")

    token = credentials.credentials
    if not token or not isinstance(token, str):
        authLogger.warning( "[getTokenFromCredential] token 值为空或不是字符串类型" )
        raise HTTPException(status_code=401, detail="用户凭证无效！")
    return token

def verifyTokenAndGetUser(token: str, db: Session) -> type [ User ] | None :
    if not isinstance(token, str) or not token.strip():
        authLogger.error("[verifyTokenAndGetUser] token参数必须为非空字符串")
        raise HTTPException(status_code=401, detail="参数错误 - token参数必须为非空字符串")

    try:
        require_fields = ["sub", "iat", "exp", "jti", "nbf", "user_id", "openid_hash", "user_type", "token_type"]
        payload = verifyTokenFormatAndGetPayload(token, require_fields)
        if not payload:
            raise HTTPException(status_code=401, detail="token格式或签名无效")
    except HTTPException:
        raise

    user_id_str = payload.get("user_id")
    openid_hash = payload.get("openid_hash")
    user_type = payload.get("user_type")
    if user_type != "wechat_user":
        authLogger.error(f"[verifyTokenAndGetUser] 令牌类型错误: 期望wechat_user，实际{user_type}")
        raise HTTPException(status_code=401, detail="token无效")

    try:
        user_id = int(user_id_str) if user_id_str else None
    except ValueError:
        authLogger.error(f"[verifyTokenAndGetUser] user_id字段无效!")
        raise HTTPException(status_code=401, detail="user_id格式无效")

    if not user_id or user_id <= 0:
        authLogger.error(f"[verifyTokenAndGetUser] user_id 无效!")
        raise HTTPException(status_code=401, detail="user_id无效")

    if not openid_hash or not isinstance(openid_hash, str) or not openid_hash.strip():
        authLogger.error(f"[verifyTokenAndGetUser] openid_hash 无效!")
        raise HTTPException(status_code=401, detail="openid_hash无效")

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.openid:
            authLogger.error(f"[verifyTokenAndGetUser] 不存在该ID的用户或用户openid不存在")
            raise HTTPException(status_code=401, detail="不存在该ID的用户或用户openid不存在")

        decrypted_openid = decrypt(user.openid)
        if not decrypted_openid:
            authLogger.error(f"[verifyTokenAndGetUser] 解密openid失败")
            raise HTTPException(status_code=401, detail="解密 openid 失败")

        expected_openid_hash = hashlib.sha256(decrypted_openid.encode()).hexdigest()
        if openid_hash != expected_openid_hash:
            authLogger.error(f"[verifyTokenAndGetUser] 令牌中的openid_hash无效")
            raise HTTPException(status_code=401, detail="令牌中的openid_hash无效")

        authLogger.info(f"[verifyTokenAndGetUser] 令牌验证通过")
        return user
    except HTTPException:
        raise
    except Exception as e:
        authLogger.error(f"[verifyTokenAndGetUser] 验证过程中发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"验证过程中发生错误 - {str(e)}")

def extractUserByVerifyCredential( credentials: HTTPAuthorizationCredentials , db: Session = Depends( get_database ) ) -> type[User]| None :
    """ 提取并验证token，从token提取用户信息，对用户信息进行校验，返回有效的用户信息！"""
    if not isinstance(db, Session):
        authLogger.warning( f"[extractUserByVerifyCredential] db 类型错误，期望的类型为 Session，实际为 {type( db ).__name__}" )
        raise TypeError("db参数类型错误！")

    try:
        token = getTokenFromCredential(credentials)
        user = verifyTokenAndGetUser(token,db)
        if not user:
            return None
        return user

    except HTTPException:
        raise
    except TypeError as e:
        authLogger.error( f"[extractUserByVerifyCredential] 参数类型错误 - {str( e )}" )
        raise HTTPException(status_code=500, detail=f"参数类型错误 - {str(e)}")
    except Exception as e:
        authLogger.error( f"[extractUserByVerifyCredential] 处理token时发生异常 - {str( e )}" )
        raise HTTPException(status_code=500, detail="处理token时发生错误")
