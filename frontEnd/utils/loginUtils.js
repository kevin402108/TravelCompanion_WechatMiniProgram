const DURATION = 1000 

// tokenObj对象：expiration_time,id,token
//检查是否注册、token是否过期
// 参数: isAppOnLaunch：判断当前是否处于载入小程序阶段 1:是,0:否
const checkLogin = (isAppOnLaunch = 0) => {
  //如果本地缓存有token,检查其是否有效，无效则刷新token
  const tokenObj = wx.getStorageSync('tokenObj')
  if (tokenObj) {
    const { id, expiration_time } = tokenObj
    //如果token过期
    if (Date.now() >= expiration_time) {
      wx.showToast({
        title: '登录过期，正在自动重新登录！',
        icon: 'none'
      })
      login()
    } else {
      if (isAppOnLaunch === 1) {
        wx.request({
          url: `http://127.0.0.1:8001/user/updateLoginTime`,
          data: {
            id: id
          },
          method: 'PUT',
          header: {
            'Content-Type': 'application/json'
          },
          timeout: 5000,
          success: (res) => {
            console.log(res);
            if (res.statusCode >= 200 && res.statusCode < 300) {
              console.log("更新用户最后登录时间成功！")
            } else{
              if(res.statusCode === 400){
                console.log("请求参数错误：")
              }
              if(res.statusCode === 404){
                wx.setStorageSync('tokenObj', null)
                console.log(`ID为${id}的用户不存在，正在重新注册！`)
                register()
              }
              if(res.statusCode === 422){
                wx.setStorageSync('tokenObj', null)
                console.log(`请求参数错误：用户ID不能小于1，正在重新注册！`)
                register()
              }
              if(res.statusCode === 500){
                console.log("服务器内部发生错误！")
                wx.showToast({
                  title: '服务器内部发生错误！',
                  icon: 'none',
                  duration: 2000
                })
              } else {
                console.log(`更新ID为${id}的用户最后登录时间时发生未知错误！`)
                wx.showToast({
                  title: '小程序发生未知错误！',
                  icon: 'none',
                  duration: 2000
                })
              }
            }
          },
          fail: (err) => {
            console.log(err);
            wx.showToast({
              title: '网络异常或连接超时！',
              icon: 'none',
              duration: 2000
            })
          }
        })
      }
    }
  } else {
    // 如果无法从本地存储中获取tokenObj,默认为新用户，直接注册
    register()
  }
}

const register = () => {
  wx.login({
    success: (res) => {
      console.log(res)
      wx.request({
        url: 'http://127.0.0.1:8001/auth/register',
        method: 'POST',
        data: {
          code: res.code
        },
        success: (res) => {
          console.log(res)
          if (res.statusCode >= 200 && res.statusCode < 300) {
            const { isNewUser, token } = res.data.data
            saveLoginInfo(token)
            if (isNewUser) {
              wx.showToast({
                title: '新用户登录成功！',
                icon: 'none',
                duration: 2000
              })
            } else {
              console.log("老用户无需注册，欢迎回来！")
              wx.showToast({
                title: '欢迎回来！',
                icon: 'none',
                duration: 2000
              })
            }
          } else {
            if(res.statusCode === 500){
                console.log("服务器内部发生错误！")
                wx.showToast({
                  title: '服务器内部发生错误！',
                  icon: 'none',
                  duration: 2000
                })
              } else {
                console.log(`用户注册时发生未知错误！`)
                wx.showToast({
                  title: '小程序发生未知错误！',
                  icon: 'none',
                  duration: 2000
                })
              }
          }
        },
        fail: (err) => {
            console.log(err);
            wx.showToast({
              title: '网络异常或连接超时！',
              icon: 'none',
              duration: 2000
            })
        }
      })
    }
  })
}

const login = () => {
  const tokenObj = wx.getStorageSync('tokenObj')
  wx.login({
    success: (res) => {
      wx.request({
        url: 'http://127.0.0.1:8001/auth/login',
        method: 'PUT',
        data: {
          id: tokenObj.id,
          code: res.code
        },
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            console.log(res)
            const { token, id } = res.data.data
            saveLoginInfo(token, id)
            wx.showToast({
              title: '登录成功',
              icon: 'none',
              duration: 2000
            })
          } else {
            console.log(res)
            wx.showToast({
              title: '登录失败',
              icon: 'none'
            })
          }
        },
        fail: (err) => {
            console.log(err);
            wx.showToast({
              title: '网络错误！',
              icon: 'none',
            })
        }
      })
    }
  })
}

//将获取的token对象存入本地缓存
const saveLoginInfo = (token) => {
  const expiration_time = Date.now() + DURATION
  const tokenObj = {
    token,
    expiration_time
  }
  wx.setStorageSync('tokenObj', tokenObj)
}

export default {
  checkLogin,
  login,
  saveLoginInfo
}