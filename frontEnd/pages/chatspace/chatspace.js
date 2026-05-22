// pages/chatspace/chatspace.js
Page({
  data: {
    tabList:['讨论旅游行程','发布帖子'],
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
  
  onLoad(options) {},
  onReady() {},
  onShow() {},
  onHide() {},
  onUnload() {},
  onPullDownRefresh() {},
  onReachBottom() {},
  onShareAppMessage() {}
})