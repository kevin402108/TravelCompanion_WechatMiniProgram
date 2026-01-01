import os
import re
import urllib
import urllib.parse
import uuid
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv
from fastapi import APIRouter , Depends , File , UploadFile , Header , HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from backEnd.app.database import get_database
from backEnd.app.utils.jwt_handler import get_user_info_from_token
from backEnd.app.utils.cos_utils import TencentCloudCOSManager
from backEnd.app.utils.logger import setup_logger

upload_router = APIRouter()
upload_logger = setup_logger( 'upload_logger')

# 上传图片接口
@upload_router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    authorization: str = Header(None),
    db: Session = Depends(get_database)
):
    try:
        # 提取用户token
        if not authorization or not isinstance(authorization, str) or not authorization.strip() or not authorization.startswith("Bearer "):
            upload_logger.error("[upload_image] header中缺少Authorization字段或Authorization字段无效")
            raise HTTPException(status_code=400, detail="header中缺少Authorization字段或Authorization字段无效")
        token = authorization.replace("Bearer ", "").strip()

        # 验证用户身份
        user_info = get_user_info_from_token(token,db)
        if not user_info or not user_info.get("valid"):
            upload_logger.error("[upload_image] token无效，用户身份验证失败！")
            raise HTTPException(status_code=401, detail="token无效，用户身份验证失败！")

        # 格式验证
        allowed_extensions = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        if file.content_type not in allowed_extensions:
            upload_logger.error(f"[upload_image] 不支持的图片格式:{file.content_type}")
            raise HTTPException(status_code=400, detail=f"不支持{file.content_type}格式的图片，支持的图片格式：jpg、jpeg、png、webp")

        # 文件大小验证(单张图片大小不得超过5MB)
        file_content = await file.read()
        if len(file_content) > 1024 * 1024 * 5:
            upload_logger.error("[upload_image] 图片文件过大，超出5MB的最大限制")
            raise HTTPException(status_code=400, detail="图片文件过大，超出最大限制，请上传不大于5MB的图片")

        await file.seek(0)
        sanitized_filename = sanitize_filename(file.filename)

    except Exception as e:
        pass

# 生成安全的文件名
def sanitize_filename (original_filename: str) :
    if not original_filename or not isinstance(original_filename, str) or not original_filename.strip():
        upload_logger.error("[sanitize_filename] original_filename参数无效！")
        return None

    pure_name = os.path.basename(urllib.parse.unquote(original_filename))
    base,ext = os.path.splitext(pure_name)
    ext = ext.lower()

    safe_base = re.sub(r'[^\w.-]', '_', base)
    safe_base = re.sub(r'\.{2,}', '_', safe_base).strip('.')

