# 封装的常用异常处理模块
from fastapi import HTTPException
from backEnd.app.utils.logger import setup_logger

# 设置异常相关的日志记录器
exception_logger = setup_logger('exception_logger')

# 处理数据库连接异常
class DatabaseConnectionError(HTTPException):
    def __init__(self, detail):
        exception_logger.error(f"数据库连接错误: {detail}")
        super().__init__(status_code=500, detail=f"数据库连接错误: {detail}")

# 处理sql执行异常
class SQLExecutionError(HTTPException):
    def __init__(self, detail):
        exception_logger.error(f"SQL 执行错误: {detail}")
        super().__init__(status_code=500, detail=f"SQL 执行错误: {detail}")

# 处理数据类型不匹配异常
class DataMismatchError(HTTPException):
    def __init__(self, detail):
        exception_logger.error(f"数据类型不匹配错误: {detail}")
        super().__init__(status_code=500, detail=f"数据类型不匹配错误: {detail}")

# 处理完整性约束异常
class IntegrityConstraintError(HTTPException):
    def __init__(self, detail):
        exception_logger.error(f"完整性约束违反错误: {detail}")
        super().__init__(status_code=500, detail=f"完整性约束违反错误: {detail}")

# 处理用户不存在异常
class UserNotFoundError(HTTPException):
    def __init__(self):
        exception_logger.error("无法查询到该用户!")
        super().__init__(status_code=404, detail="无法查询到该用户!")

# 处理其他未知异常
class UnknownError(HTTPException):
    def __init__(self, detail):
        exception_logger.error(f"未知错误: {detail}")
        super().__init__(status_code=500, detail=f"未知错误: {detail}")