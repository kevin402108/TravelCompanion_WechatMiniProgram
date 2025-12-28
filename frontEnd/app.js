import './utils/lodash-fix'
import versionUtils from './utils/versionUtils'
import loginUtils from './utils/loginUtils'

App({
    globalData: {
      LocalSDKVersion: null,
      MIN_SDK_VERSION: '3.2.5',
      PRIVACY_CONTRACT_NAME: '旅伴奇遇工坊隐私保护指引',
      DEFAULT_AVATAR_URL: "https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0",
      isSuitableVersion: false,
      resolvePricay: null,
      isUserLogin: false
    },

    onLaunch: function () {
      const LocalSDKVer = versionUtils.getLocalSDKVersion()
      this.globalData.LocalSDKVersion = LocalSDKVer
      this.globalData.isUserLogin = false
      //检查用户登录情况
      loginUtils.checkLogin(this)
    },

    getLoginStatus: function(){
      return this.globalData.isUserLogin
    },

    setLoginStatus: function(status){
      this.globalData.isUserLogin = status
    }
});
