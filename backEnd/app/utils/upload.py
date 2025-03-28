import os
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from backEnd.app.models import User
from backEnd.app.database import get_database
from backEnd.app.utils import exceptions
from backEnd.app.utils.logger import setup_logger
from sqlalchemy.orm import Session

upload_router = APIRouter()
logger = setup_logger('upload_logger')

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
    
    try:
        user = db.query(User).filter(User.id == id).first()
        if not user:
            logger.error("用户不存在")
            return exceptions.UserNotFoundError()
        else:
            file_name = image_files.filename
            file_url = f"http://127.0.0.1:8001/user/avatar?pic_name={file_name}"

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