import os
import logging

# 日志文件名
LOG_FILE = "app.log"
# 当前文件所在的目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR))))

def setupLogger( name , fileName=LOG_FILE , level=logging.INFO ):
    """
    设置日志记录器
    :param name: 日志记录器的名称
    :param log_file: 日志文件的路径
    :param level: 日志级别，默认为 INFO
    :return: 配置好的日志记录器
    """

    file_abs_path = os.path.join(ROOT_DIR,"logs",fileName)

    # 确保存放日志文件的目录存在
    log_dir = os.path.dirname(file_abs_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 创建文件处理器,并设置日志格式
    file_handler = logging.FileHandler(file_abs_path)
    file_handler.setFormatter(formatter)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 设置日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger