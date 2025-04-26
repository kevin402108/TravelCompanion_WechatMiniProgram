// pages/routeGen/routeGen.js
Page({
  data: {
    destination: '',
    travelDays: '',
    budget: '',
    preferences: '',
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

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    this.setData({
      budget: 0,
      travelDays:0
    })
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {},

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {},

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {},

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {},

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {},

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {},

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {},
});
