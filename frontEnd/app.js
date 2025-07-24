import loginUtils from './utils/loginUtils'

App({
  globalData: {
    LocalSDKVersion:null,
    MIN_SDK_VERSION:'3.2.5',
    PRIVACY_CONTRACT_NAME:'旅伴奇遇工坊隐私保护指引',
    DEFAULT_AVATAR_URL:"https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0",
    isSuitableVersion:false,
    resolvePricay:null
  },

  onLaunch: function () {
    //检查用户登录情况
    loginUtils.checkLogin(1)
  }
});
