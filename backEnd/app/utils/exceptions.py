# 封装的常用异常处理模块
from fastapi import HTTPException
from backEnd.app.utils.logger import setupLogger

# 设置异常相关的日志记录器
exception_logger = setupLogger( "exception_logger" )


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
        super().__init__(status_code=409, detail=f"完整性约束违反错误: {detail}")


# 处理用户不存在异常
class UserNotFoundError(HTTPException):
    def __init__(self):
        exception_logger.error("无法查询到该用户!")
        super().__init__(status_code=404, detail="无法查询到该用户!")


#  处理微信API调用失败异常
class WechatAPIRequestError(HTTPException):
    def __init__(self, detail: str):
        exception_logger.error(f"微信API调用失败: {detail}")
        super().__init__(status_code=500, detail=f"微信API调用失败: {detail}")


#  处理微信API密钥错误异常
class WechatAPIKeyError(HTTPException):
    def __init__(self, detail):
        exception_logger.error(f"KeyError: {detail}")
        super().__init__(status_code=500, detail=f"KeyError: {detail}")


# 处理JSON解析失败异常
class JSONDecodeError(HTTPException):
    def __init__(self, detail):
        exception_logger.error(f"JSON解析失败: {detail}")
        super().__init__(status_code=500, detail=f"JSON解析失败: {detail}")


class DataError(HTTPException):
    def __init__(self, detail):
        exception_logger.error(f"数据错误: {detail}")
        super().__init__(status_code=400, detail=f"数据错误: {detail}")


# 处理其他未知异常
class UnknownError(HTTPException):
    def __init__(self, detail):
        exception_logger.error(f"未知错误: {detail}")
        super().__init__(status_code=500, detail=f"未知错误: {detail}")


class SpotIDListConversionError(HTTPException):
    def __init__(self, original_error: Exception, invalid_str: str, pos: int):
        self.error_type = type(original_error).__name__
        self.pos = pos + 1
        self.invalid_str = invalid_str
        self.original_error = original_error
        error_msg = f"景点列表转换失败于第{self.pos}个元素:'{invalid_str}'\
            ({self.error_type}:{str(original_error)})"

        exception_logger.error(error_msg)
        super().__init__(status_code=400, detail=error_msg)
