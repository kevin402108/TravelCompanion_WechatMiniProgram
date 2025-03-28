const DURATION = 8640000 //token有效期 单位：ms

// tokenObj对象：expiration_time,id,token
//检查是否注册、登录态、token有无、token是否过期
const checkLogin = () => {
  //如果本地缓存有token,检查其是否有效，无效则刷新token
  const tokenObj = wx.getStorageSync('tokenObj')
  const loginStatus = wx.getStorageSync('loginStatus')
  if (tokenObj) {
    const { token, id, expiration_time } = tokenObj
    //如果token过期
    if ( Date.now() >= expiration_time) {
      wx.showToast({
        title: '登录过期，正在自动重新登录！',
        icon: 'none'
      })
      wx.setStorageSync('loginStatus', 0)
      login()
    } else {
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
          if (res.statusCode === 200) {
            console.log("用户最后登录时间更新成功")
          } else {
            wx.showToast({
              title:'无法同步最后登录时间',
              icon:'none',
              duration:2000
            })
          }
        }
      })
    }

  } else {
    //如果无法从本地存储中获取tokenObj,默认为新用户，直接注册
    register()
  }
}

const register = () => {
  wx.login({
    success: (res) => {
      wx.request({
        url: 'http://127.0.0.1:8001/auth/register',
        method: 'POST',
        data: {
          code: res.code
        },
        success: (res) => {
          console.log(res)
          if (res.statusCode >= 200 && res.statusCode < 300) {
            const { loginStatus, token, id } = res.data.data
            saveLoginInfo(token, loginStatus, id)
          } else {
            wx.showToast({
              title: '登录失败',
              icon: 'none'
            })
          }

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
            const { loginStatus, token, id } = res.data.data
            saveLoginInfo(token, loginStatus, id)
          } else {
            wx.showToast({
              title: '登录失败',
              icon: 'none'
            })
          }
        }
      })
    }
  })
}

//将获取的token对象存入本地缓存
const saveLoginInfo = (token, loginStatus, id) => {
  const expiration_time = Date.now() + DURATION
  const tokenObj = {
    id,
    token, //token
    expiration_time //过期时间
  }
  wx.setStorageSync('tokenObj', tokenObj)
  wx.setStorageSync('loginStatus', loginStatus) //登录态
}

export default {
  checkLogin,
  login,
  saveLoginInfo
}