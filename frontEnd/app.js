import loginUtils from './utils/loginUtils'

App({
  globalData: {
    defaultAvatarUrl:
      "https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0",
  },

  onLaunch: function () {
    // 启动uvicorn服务
    const url = "http://127.0.0.1:8002"
    wx.request({
      url:`${url}/start_uvicorn`,
      method:'GET',
      success: function(res) {
        console.log("uvicorn服务启动成功!",res.data)
      },
      fail: function(err) {
        console.log("uvicorn启动失败！")
        console.log(err)
      }
    })

    //检查用户登录情况
    loginUtils.checkLogin()
  },
});
