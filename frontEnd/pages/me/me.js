import loginUtils from "../../utils/loginUtils"
const app = getApp();

Page({
  data: {
    user: {
      id: '',
      token: '',
      nickname: "微信用户",
      avatar: app.globalData.defaultAvatarUrl,
    },
  },

  editInfo() {
    wx.navigateTo({
      url: "/pages/me/personalInfo/personalInfo",
    });
  },

  //功能：获取用户昵称和头像，以便渲染页面时展示用户信息
  getUserInfo() {
    //从本地缓存中尝试获取获取登录状态loginStatus和用户token信息
    let tokenObj = wx.getStorageSync('tokenObj')
    const loginStatus = wx.getStorageSync('loginStatus')

    //若无法从localStorage找到tokenObj/token失效/loginStatus,则进行登录
    if (!tokenObj || tokenObj.expiration_time <= Date.now() || !loginStatus || !tokenObj.token) {
      // console.log("登录过期或未登录！")
      loginUtils.login()
      tokenObj = wx.getStorageSync('tokenObj')
    }

    wx.showNavigationBarLoading()
    //通过token获取用户头像和昵称 GET请求
    wx.request({
      url: `http://127.0.0.1:8001/user/profile`,
      data: {
        id: tokenObj.id
      },
      timeout: 5000,
      success: (res) => {
        console.log(res)
        wx.hideNavigationBarLoading()
        if (res.statusCode == 200) {
          const { avatar, nickname } = res.data.data.userInfo
          this.setData({
            user: {
              avatar: avatar || app.globalData.defaultAvatarUrl,
              nickname
            }
          })
        } else {
          wx.hideNavigationBarLoading();
          wx.showToast({
            title: "获取用户信息失败！",
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideNavigationBarLoading();
        wx.showToast({
          title: "获取用户信息失败！",
          icon: 'none'
        })
        this.setData({
          user: {
            nickname: "微信用户",
            avatar: app.globalData.defaultAvatarUrl
          },
        });
      },
    })
  },

  onLoad(options) {},

  /*生命周期函数--监听页面初次渲染完成*/
  onReady() { },

  /*生命周期函数--监听页面显示*/
  onShow() {
    //若从别的页面nevigateBack回该页面，重新获取用户信息并渲染到页面上
    this.getUserInfo()
  },

  /* 生命周期函数--监听页面隐藏*/
  onHide() { },

  /*生命周期函数--监听页面卸载*/
  onUnload() { },

  /*页面相关事件处理函数--监听用户下拉动作*/
  onPullDownRefresh() { },

  /*页面上拉触底事件的处理函数*/
  onReachBottom() { },

  /*用户点击右上角分享*/
  onShareAppMessage() { },
});
