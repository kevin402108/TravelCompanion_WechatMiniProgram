// frontend/utils/loginUtils.js
import {writeLog} from "./loggerUtils";

const DURATION = 1800000

/**
 * 检查用户登录状态，并执行相应的操作。
 * @param {App} appInstance - 应用实例
 **/
// tokenObj对象：isNewUser, token, token_expired_at
const checkLogin = (appInstance=null) => {
  const tokenObj = wx.getStorageSync('tokenObj')
  if (tokenObj) {
    const { isNewUser, token, token_expired_at } = tokenObj

    // 验证tokenObj
    if(!isValidToken(token) || !token_expired_at || typeof token_expired_at !== 'number'){
      writeLog('checkLogin', 'ERROR', 'isNewUser状态不正确，跳转至认证流程')
      appInstance.setLoginStatus(false)
      auth(appInstance)
    } else if (Date.now() >= token_expired_at) {
      writeLog('checkLogin', 'WARNING', 'token过期，正在自动重新认证')
      wx.showToast({
        title: '登录过期，正在自动重新登录！',
        icon: 'none'
      })
      appInstance.setLoginStatus(false)
      auth(appInstance)
    } else {
      if(typeof isNewUser !== 'boolean') {
        writeLog('checkLogin', 'ERROR', 'isNewUser状态不正确，跳转至认证流程')
        appInstance.setLoginStatus(false)
        auth(appInstance)
      } else {
        writeLog('checkLogin', 'INFO', '登录状态检查通过，设置全局登录状态为true')
        appInstance.setLoginStatus(true)
      }
    }
  } else {
    // 如果无法从本地存储中获取tokenObj
    writeLog('checkLogin', 'INFO', '未找到tokenObj，开始认证流程')
    appInstance.setLoginStatus(false)
    auth(appInstance)
  }
}

/**
 * 认证流程 - 识别用户身份并区分新老用户
 * @param {App} appInstance - 应用实例
 */
const auth = (appInstance=null) =>{
    wx.showLoading({
      title: '加载中...',
      mask: true
    })
    wx.login({
      success: (res) => {
        if(res.code){
          writeLog('auth', 'INFO', '获取登录凭证成功，发送至后端验证')
          wx.request({
            url: 'http://127.0.0.1:8001/auth',
            method: 'POST',
            data: {
              code: res.code
            },
            success: (res) => {
              wx.hideLoading()
              if(res.statusCode >= 200 && res.statusCode < 300){
                const {isNewUser, token, token_expired_at} = res.data.data
                if(isNewUser) {
                  writeLog('auth', 'INFO', '新用户认证成功，保存临时状态并执行登录流程');
                  // 保存新用户临时状态
                  if(!saveLoginInfo(null,true,null)){
                    writeLog('auth', 'ERROR', '保存临时状态失败')
                    wx.showToast({
                        title: '认证时发生错误，请稍后重试！',
                        icon: 'none',
                        duration: 2000
                    })
                    return
                  }
                  appInstance.setLoginStatus(false)
                  wx.showToast({
                    title: '新用户,欢迎使用本小程序！',
                    icon: 'none',
                    duration: 2000
                  })
                  login(appInstance)
                } else {
                  if (!isValidToken(token) || !token_expired_at || typeof token_expired_at !== 'number'
                      || token_expired_at*1000 <= Date.now()) {
                    writeLog('auth', 'ERROR', 'token或过期时间无效')
                    appInstance.setLoginStatus(false)
                    wx.showToast({
                      title: '认证时发生错误，请稍后重试！',
                      icon: 'none',
                      duration: 2000
                    })
                    return
                  }
                  writeLog('auth', 'INFO', '老用户认证成功，保存完整token信息')
                  // 保存老用户完整信息
                  if(!saveLoginInfo(token, false, token_expired_at)){
                    writeLog('auth', 'ERROR', '保存完整token信息失败')
                    wx.showToast({
                        title: '认证时发生错误，请稍后重试！',
                        icon: 'none',
                        duration: 2000
                    })
                    return
                  }
                  appInstance.setLoginStatus(true)
                }
              } else {
                appInstance.setLoginStatus(false)
                if(res.statusCode === 400){
                  writeLog('auth', 'ERROR', `参数错误: ${res.data.detail || 'code参数无效'}`)
                  wx.showToast({
                    title: '用户登录凭证无效，请稍后重试！',
                    icon: 'none',
                    duration: 2000
                  })
                } else if(res.statusCode === 500){
                  writeLog('auth', 'ERROR', '服务器内部发生错误')
                  wx.showToast({
                    title: '服务器异常，请稍后重试！',
                    icon: 'none',
                    duration: 2000
                  })
                } else {
                  writeLog('auth', 'ERROR', '用户认证时发生未知错误')
                  wx.showToast({
                    title: '小程序发生未知错误，请稍后重试！',
                    icon: 'none',
                    duration: 2000
                  })
                }
              }
            },
            fail:(err) =>{
              appInstance.setLoginStatus(false)
              wx.hideLoading()
              writeLog('auth', 'ERROR', '网络异常或连接超时')
              wx.showToast({
                title: '网络异常或连接超时，请检查网络连接后重试',
                icon: 'none',
                duration: 2000
              })
            }
          })
        } else {
          appInstance.setLoginStatus(false)
          wx.hideLoading()
          writeLog('auth', 'ERROR', '获取登录凭证失败')
          wx.showToast({
            title: '获取登录凭证失败,请稍后重试！',
            icon: 'none',
            duration: 2000
          })
        }
      },
      fail:(err) =>{
        appInstance.setLoginStatus(false)
        wx.hideLoading()
        writeLog('auth', 'ERROR', `${err.errMsg}`)
        wx.showToast({
          title: '获取登录凭证失败,请检查网络连接后重试！',
          icon: 'none',
          duration: 2000
        })
      }
    })
}

const login = (appInstance=null) => {
  wx.showLoading({
    title: '登录中...',
    mask: true
  })
  wx.login({
    success: (res) => {
      if(res.code){
        writeLog('auth', 'INFO', '获取登录凭证成功，发送至后端验证')
        wx.request({
          url: 'http://127.0.0.1:8001/login',
          method: 'POST',
          data: {
            code: res.code
          },
          success: (res) => {
            if(res.statusCode >= 200 && res.statusCode < 300){
              wx.hideLoading()
              const {success, token, token_expired_at} = res.data.data
              if(success && token && token_expired_at) {
                // 登录成功，保存完整信息并设置全局已登录状态
                if (!isValidToken(token) || !token_expired_at || typeof token_expired_at !== 'number'
                    || token_expired_at*1000 <= Date.now()) {
                  writeLog('auth', 'ERROR', 'token或过期时间无效')
                  appInstance.setLoginStatus(false)
                  wx.showToast({
                    title: '登录时发生错误，请稍后重试！',
                    icon: 'none',
                    duration: 2000
                  })
                   return
                }
                saveLoginInfo(token,false,token_expired_at)
                appInstance.setLoginStatus(true)
                writeLog('auth', 'INFO', '登录成功，保存完整token信息')
                wx.showToast({
                  title: '登录成功！',
                  icon: 'none',
                  duration: 2000
                })
              } else {
                writeLog('login', 'ERROR', '登录返回数据不完整');
                appInstance.setLoginStatus(false)
                wx.showToast({
                  title: '登录失败，请稍后重试!',
                  icon: 'none',
                  duration: 2000
                })
              }
            } else {
              appInstance.setLoginStatus(false)
              writeLog('login', 'ERROR', `登录失败 - ${res.statusCode}:${res.data.detail || '未知错误'}`);
              wx.showToast({
                title: '登录失败，请稍后重试!',
                icon: 'none',
                duration: 2000
              })
            }
          },
          fail:(err) =>{
            appInstance.setLoginStatus(false)
            wx.hideLoading()
            writeLog('login', 'ERROR', '网络异常或连接超时')
            wx.showToast({
              title: '登录失败，请检查网络连接！',
              icon: 'none',
              duration: 2000
            })
          }
        })
      } else {
        appInstance.setLoginStatus(false)
        writeLog('login', 'ERROR', '获取登录凭证失败')
        wx.showToast({
          title: '获取登录凭证失败，请检查网络连接！',
          icon: 'none',
          duration: 2000
        })
      }
    },
    fail:(err) =>{
      appInstance.setLoginStatus(false)
      wx.hideLoading()
      writeLog('login', 'ERROR', `${err.errMsg}`)
      wx.showToast({
        title: '获取登录凭证失败，请检查网络连接！',
        icon: 'none',
        duration: 2000
      })
    }
  })
}

//将获取的token对象存入本地缓存
const saveLoginInfo = (token,isNewUser=false,token_expired_at=null) => {
  if(typeof isNewUser !== 'boolean') return false;
  if(token_expired_at && !(typeof token_expired_at === 'number')) return false;
  if(token_expired_at && token_expired_at*1000 <= Date.now()) return false;
  if(token&&!isValidToken(token)) return false;
  const tokenObj = {
    token,
    isNewUser,
    token_expired_at
  }
  wx.setStorageSync('tokenObj', tokenObj)
  return true
}

// 初步验证token格式是否正确
const isValidToken = (token) => {
  if (!token || typeof token !== 'string') return false;
  const parts = token.split('.');
  if (parts.length !== 3) return false;

  const PATTERN = /^[A-Za-z0-9-_]+$/;
  if (!parts.every(part => PATTERN.test(part))) return false;

  try {
    const payloadStr = atob(parts[1]);
    if (!payloadStr) throw new Error('Empty payload');

    let payload;
    try {payload = JSON.parse(payloadStr);}
    catch (e) {throw new Error('Invalid JSON in payload');}

    if (typeof payload !== 'object' || payload === null) return false;
    const now = Math.floor(Date.now() / 1000);

    // 必要字段校验
    if (!payload.sub || typeof payload.sub !== 'string') return false;
    if (!payload.exp || typeof payload.exp !== 'number' || payload.exp < now) return false;
    if (!payload.iat || typeof payload.iat !== 'number' || payload.iat > now) return false;
    if (!payload.nbf || typeof payload.nbf !== 'number' || payload.nbf > now) return false;
    if (!payload.jti || typeof payload.jti !== 'string') return false;

    // 业务字段校验
    const userIdNum = Number(payload.user_id);
    if (isNaN(userIdNum) || userIdNum <= 0) return false;
    if (!payload.openid_hash || typeof payload.openid_hash !== 'string') return false;
    if (!payload.user_type || typeof payload.user_type !== 'string' || payload.user_type !== 'wechat_user') return false;
    if (!payload.token_type || typeof payload.token_type !== 'string' || payload.token_type !== 'user_access') return false;

    return true;
  } catch (e) {
    writeLog('auth', 'ERROR', `Token validation failed: ${e.message}`);
    console.error(e);
    return false;
  }
};

export default {
  checkLogin,
  login,
  saveLoginInfo
}