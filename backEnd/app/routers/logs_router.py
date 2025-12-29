import os
import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from backEnd.app.utils.logger import setup_logger

# 定义后端专门接受前端日志的日志记录器
logger = setup_logger('frontend_logger', fileName='frontend.log')

# 定义处理前端日志专用路由
frontend_logs_router = APIRouter()

@frontend_logs_router.post("/write")
async def write_log(request: Request):
    try:
        # 获取请求体中的 JSON 数据
        log_data = await request.json()
        name = log_data.get('name', 'frontend')  # 日志记录器名称
        level = log_data.get('level', 'INFO').upper()  # 日志级别
        message = log_data.get('message','')  # 日志信息

        if not message:
            logger.warning("缺少 'message' 字段")
            raise ValueError("缺少 'message' 字段")

        # 映射日志级别
        level_mapping = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

        log_level = level_mapping.get(level, logging.INFO)

        # 记录日志，使用与前端相同的格式
        logger.log(level=log_level, msg=message)
        return JSONResponse(content={"status": "success", "message": "日志已记录"}, status_code=200)
    except Exception as e:
        # 如果发生错误，记录错误日志并返回 500
        logger.error(f"处理前端日志时发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"处理日志时发生错误: {e}")