// pages/chatspace/chatspace.js
Page({
  data: {
    tabList:['讨论旅游行程','帖子广场','发布帖子'],
    tabIndex:0,
    msgContent:'',
    postContent:''  
  },

  onTabClick(e) {
    const index = +e.currentTarget.id
    this.setData({
      tabIndex:index
    })
  },
  
  onMsgSend() {
    wx.showToast({
      icon:'none',
      title:'消息发送成功！'
    })
    this.setData({
      msgContent:''
    })
    
  },

  submitPost() {
    wx.showToast({
      icon:'success',
      title:'发布成功！'
    })
    this.setData({
      postContent:''
    })
  },
  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  }
})