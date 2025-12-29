// frontend/utils/loggerUtils.js

/**
 *信息到后端日志记录接口。
 * @param {string} name - 日志记录器的名称，默认为 'frontend'。
 * @param {string} level - 日志级别，默认为 'INFO'，可选 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'。
 * @param {string} message - 要记录的日志信息。
 */
const writeLog = (name = 'frontend', level = 'INFO', message) => {
  // 构建日志数据
  const logData = {
    name: name,
    level: level,
    message: message
  };

  // 使用 wx.request() 发送日志数据到后端日志接口
  wx.request({
    url: 'http://127.0.0.1:8001/logs/write/',
    method: 'POST',
    header:{
      'Content-Type': 'application/json'
    },
    data: logData,
    success: (res) => {
      // console.log(res)
      if (res.statusCode >= 200 && res.statusCode < 300) {
        // console.log('writeLog: 日志已成功发送到后端');
      } else {
        console.error(`writeLog: 日志写入失败，状态码: ${res.statusCode}`);
      }
    },
    fail: (err) => {
      // console.log(err)
      console.error(`writeLog: 发送日志时发生错误: ${err.errMsg}`);
    }
  });
};

export {
  writeLog
};