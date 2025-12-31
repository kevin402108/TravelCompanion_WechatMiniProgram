import requestUtils from "../../utils/requestUtils";
import loginUtils from "../../utils/loginUtils";
import {writeLog} from "../../utils/loggerUtils";
const app = getApp();

Page({
  data: {
      user: {
        nickname: '',
        avatar: app.globalData.DEFAULT_AVATAR_URL,
      },
      isLogin: false
  },

  editInfo() {
    if(!this.data.isLogin) {
        this.getUserInfo();
        return;
    }
    wx.navigateTo({
      url: "/pages/me/personalInfo/personalInfo",
    });
  },

  //功能：获取用户昵称和头像，以便渲染页面时展示用户信息
  getUserInfo() {
    wx.showNavigationBarLoading();
    requestUtils.requestWithAuth('http://127.0.0.1:8001/user/profile', {
      method: "GET",
      timeout: 5000,
    }).then((res) =>{
        console.log(res)
       wx.hideNavigationBarLoading();
       if (res.statusCode >= 200 && res.statusCode < 300) {
         const { nickname, avatar } = res.data.data.userInfo;
         this.setData({
             user: {
               avatar: avatar || app.globalData.DEFAULT_AVATAR_URL,
               nickname
             },
             isLogin: true
         });
         writeLog('个人中心','INFO','获取用户信息成功!')
       } else {
         if (res.statusCode === 401) {
             writeLog('个人中心','ERROR','获取用户信息失败 - 用户认证失败，token无效或已过期')
             wx.showToast({
               title: "登录已过期，正在重新登录",
               icon: 'none',
               duration: 2000,
             });
             loginUtils.checkLogin(app);
         } else {
             writeLog('个人中心','ERROR',`获取用户信息失败 - 错误状态码:${res.statusCode},错误详情：${res.data}`)
             wx.showToast({
               title: "获取用户信息时出错,请稍后重试！",
               icon: 'none',
               duration: 2000
             });
         }
       }
    }).catch((err)=>{
        wx.hideNavigationBarLoading();
        if(err.errMsg) {
            writeLog('个人中心','ERROR',`获取用户信息失败 - 错误信息:${err.errMsg}`)
            wx.showToast({
                title: "网络错误，请检查网络连接后重试！",
                icon: 'none',
                duration: 2000,
            });
        } else if (err.message && err.message.includes('Authentication required')) {
            writeLog('个人中心','ERROR',`获取用户信息失败 - 需要用户登录`)
            return requestUtils.showLoginGuideModal();
        } else {
            console.error('获取用户信息时发生错误:', err);
            wx.showToast({
                title: "获取用户信息失败，请稍后再试！",
                icon: 'none',
                duration: 2000
            });
        }

        this.setData({
            user: {
              nickname: '',
              avatar: app.globalData.DEFAULT_AVATAR_URL,
            },
            isLogin: false
        });
    })
  },

  onLoad(options) {
      const isUserLogin = app.getLoginStatus()
      if(isUserLogin) {
          this.setData({
              isLogin: true
          })
      }
      if(this.data.isLogin) {
          this.getUserInfo()
      }
  },
  onReady() {},
  onShow() {},
  onHide() {},
  onUnload() { },
  onPullDownRefresh() { },
  onReachBottom() { },
  onShareAppMessage() { },
});
