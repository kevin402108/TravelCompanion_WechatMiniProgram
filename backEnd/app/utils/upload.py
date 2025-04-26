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
    id: str = Form(...),
    image_files: UploadFile = File(...),
    db:Session = Depends(get_database)
):
    if not id or not id.strip():
        logger.error("上传图片时，用户id为空")
        raise HTTPException(status_code=400, detail="用户id不能为空")
    
    try:
        id  = int(id)
        if id <= 0 :
            logger.error("用户id必须为正整数")
            return JSONResponse(status_code=400, content={"message": "用户id必须为正整数"})
    except ValueError:
        logger.error("用户id必须为整数")
        return JSONResponse(status_code=400, content={"message": "用户id必须为整数"})
    
    user = db.query(User).filter(User.id == id).first()
    if not user:
        logger.error("用户不存在")
        return exceptions.UserNotFoundError()
    
    try: 
        new_filename = sanitize_filename(image_files.filename)
        file_ext = os.path.splitext(new_filename)[1][1:]
        if file_ext not in {'jpg','jpeg','png','webp'}:
            raise HTTPException(400,"仅支持jpg/jpeg/png/webp格式的图片")
        if not image_files.content_type.startswith("images/"):
            raise HTTPException(400,"文件类型不合适")
        
        user_dir= UPLOAD_DIR / str(id)
        user_dir.mkdir(exist_ok=True)
        file_path = user_dir / new_filename
        
        async with aiofiles.open((file_path),"wb") as f:
            while chunk := await image_files.read(1024*1024):
                await f.write(chunk)
                
        encode_origin = quote(image_files.filename)
        file_url = f"/static/uploads/{id}/{new_filename}?orgin={encode_origin}"

        # 返回图片上传成功响应
        response_data = {
            "data":{
                "message": "图片上传成功",
                "image_urls": file_url
            }
        }
        return JSONResponse(status_code=200, content=response_data) 

    except Exception as e:
        logger.error(f"上传图片时发生错误：{e}")
        return JSONResponse(status_code=500, content={"message": f"上传图片时发生错误：{str(e)}"})