import './utils/lodash-fix'
import versionUtils from './utils/versionUtils'
import requestUtils from "./utils/requestUtils";
import loginUtils from './utils/loginUtils'

App({
    globalData: {
        LocalSDKVersion: null,
        MIN_SDK_VERSION: '3.2.5',
        PRIVACY_CONTRACT_NAME: '旅伴奇遇工坊隐私保护指引',
        DEFAULT_AVATAR_URL: "https://img-storage-1336210390.cos.ap-guangzhou.myqcloud.com/%E6%97%85%E8%A1%8C.png",
        isSuitableVersion: false,
        resolvePricay: null,
        isUserLogin: true
    },

    onLaunch: function () {
      const LocalSDKVer = versionUtils.getLocalSDKVersion()
      this.globalData.LocalSDKVersion = LocalSDKVer
      // this.globalData.isUserLogin = false;
      // loginUtils.checkLogin(this);
    },

    getLoginStatus: function(){
      return this.globalData.isUserLogin
    },

    setLoginStatus: function(status){
      this.globalData.isUserLogin = status
    },
});
