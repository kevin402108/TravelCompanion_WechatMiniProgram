from datetime import datetime
import os
from pathlib import Path
import re
from urllib.parse import quote, unquote
import urllib.parse
import uuid
import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import urllib
from backEnd.app.models import User
from backEnd.app.database import get_database
from backEnd.app.utils import exceptions
from backEnd.app.utils.logger import setup_logger
from sqlalchemy.orm import Session


upload_router = APIRouter()
logger = setup_logger('upload_logger')

# 配置静态文件名
UPLOAD_DIR = Path("static/uploads/avatars")
UPLOAD_DIR.mkdir(parents=True,exist_ok=True)

# 创建文件路由
upload_router.mount("/static",StaticFiles(directory="static"),name="static")

# 替换图片文件名中的特殊字符
def sanitize_filename(original_name:str)->str :
    # 提取文件名
    pure_name = os.path.basename(urllib.parse.unquote(original_name))
    
    # 分割基础名和扩展名
    base,ext = os.path.splitext(pure_name)
    ext = ext.lower()
    
    # 替换非法字符
    safe_base = re.sub(r'[^\w.-]','_',base)
    safe_base = re.sub(r'\.{2,}','_',safe_base).strip('.')
    
    # 生成唯一标识
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex
    final_name = f"{safe_base}_{timestamp}_{unique_id}{ext}"
    
    return final_name
    

# 上传图片接口
@upload_router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    token: str = None
):
    pass
