// pages/routeGen/routeGen.js
Page({
  data: {
    destination: '',
    travelDays: '',
    budget: '',
    preferences: '',
  },

  navigateToAIPlan() {
    wx.navigateTo({
      url: '/pages/ai-chat/ai-chat',
    });
  },

  navigateToHistory() {
    wx.navigateTo({
      url: '/pages/historyRoutes/historyRoutes'
    });
  },

  //多个滑块共用此函数，用所点击滑块的id来区别设置的数据项
  onSliderChange(e) {
    const typeId = e.target.id;
    this.setData({
      [typeId]: e.detail.value
    })
  },

  // 提交表单
  submitForm: function () {
    const { destination, travelDays, preferences } = this.data;

    if (!destination) {
      wx.showToast({
        title: "请填写旅游目的地！",
        icon:'none',
        duration:2000
      })
      return
    }
    if (travelDays === 0) {
      wx.showToast({
        title: "请选择旅行天数！",
        icon:'none',
        duration:2000
      })
      return
    }

    if (!preferences) {
      wx.showToast({
        title: "请填写旅行偏好！",
        icon:'none',
        duration:2000
      })
      return
    }

    //携带本页面表单值跳转到生成结果页面
    const queryStr = Object.keys(this.data)
      .map((key) => `${key}=${encodeURIComponent(this.data[key])}`)
      .join("&");
    wx.redirectTo({
      url: "/pages/routeGen/routeGenResult/routeGenResult?" + queryStr,
    })
  },

  // 重置表单
  resetForm: function () {
    this.setData({
      destination: '',
      travelDays:'',
      budget: '',
      preferences: '',
    })
  },
  
  onLoad(options) {
    this.setData({
      budget: 0,
      travelDays:0
    })
  },
  onReady() {},
  onShow() {},
  onHide() {},
  onUnload() {},
  onPullDownRefresh() {},
  onReachBottom() {},
  onShareAppMessage() {}
});
