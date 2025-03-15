from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from backEnd.app.database import get_database

db_router = APIRouter()

# 手动测试数据库连接
@db_router.get("/ping_db")
def ping_db(db: Session = Depends(get_database)):
    try:
        result = db.execute(text("SHOW TABLES"))
        # 从查询结果中提取表名
        tables = [row[0] for row in result.fetchall()]  
        return {"result": tables, "status": "数据库连接成功"}
    except Exception as  e:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {e}")
    finally:
        db.close()