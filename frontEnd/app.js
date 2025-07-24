import loginUtils from './utils/loginUtils'
import versionUtils from './utils/versionUtils'
import CallCheckUtils from './utils/callCheckUtils'

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
    //获取用户微信客户端基础库版本
    const LocalSDKVer = versionUtils.getLocalSDKVersion()
    this.globalData.LocalSDKVersion = LocalSDKVer

    
    //检查用户登录情况
    loginUtils.checkLogin(1)
  }
});
