const app = getApp()
Page({
  data: {
    tabList: ['我加入的', '我发起的', '我发布的'],
    tabIndex: 0
  },

  onTabClick(e) {
    const { tabList } = this.data
    const index = +e.currentTarget.id
    this.setData({
      tabIndex: index
    })
    wx.setNavigationBarTitle({
      title: tabList[index],
    })
  },


  onLoad(options) {
    const { tabList } = this.data
    const { column } = options
    this.setData({
      tabIndex: +column
    })
    wx.setNavigationBarTitle({
      title: tabList[+this.data.tabIndex],
    })
  },
  onReady() {},
  onShow() {},
  onHide() {},
  onUnload() {},
  onPullDownRefresh() {},
  onReachBottom() {},
  onShareAppMessage() {}
})