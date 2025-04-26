import loginUtils from './utils/loginUtils'

App({
  globalData: {
    defaultAvatarUrl:
      "https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0",
  },

  onLaunch: function () {
    //检查用户登录情况
    loginUtils.checkLogin(1)
    
  },
});
