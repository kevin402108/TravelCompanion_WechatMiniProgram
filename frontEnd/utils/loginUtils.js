const DURATION = 10000

//检查登录态、token有无、token是否过期
const checkLogin = ()=>{
    //如果本地缓存有token,检查其是否有效，无效则刷新token
    const tokenObj = wx.getStorageSync('tokenObj')
    const loginStatus = wx.getStorageSync('loginStatus')
    if(tokenObj&&loginStatus){
      const curTime = Date.now()
      const {expiration_time} = tokenObj
      if(curTime >= expiration_time){
        wx.setStorageSync('loginStatus',0)
        login()
      }
    } else {
      //如果本地没有token,发请求从后台获取token
      login()
    }
}

const login = ()=>{
    wx.login({
      success:(res)=>{
        wx.request({
          url:'http://127.0.0.1:8001/auth/login',
          method:'POST',
          data:{
            code:res.code
          },
          success:(res)=>{
            console.log(res)
            const {loginStatus,token} = res.data.data
            saveLoginInfo(token,loginStatus)
          }
        })
      }
    })
}

  //将获取的token对象存入本地缓存
const saveLoginInfo = (token,loginStatus)=>{
    const expiration_time = Date.now()+DURATION
    const tokenObj = {
      token, //token
      expiration_time //过期时间
    }
    wx.setStorageSync('tokenObj', tokenObj) 
    wx.setStorageSync('loginStatus',loginStatus) //登录态
}

export default {
    checkLogin,
    login,
    saveLoginInfo
}