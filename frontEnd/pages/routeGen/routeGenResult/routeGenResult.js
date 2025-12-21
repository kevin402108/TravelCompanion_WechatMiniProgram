import loginUtils from '../../../utils/loginUtils'
const app = getApp()

Page({
  data: {
    tip: '',
    destination: '',
    travelDays: '',
    budget: '',
    preferences: '',
    route: '',
    tipShow: true,
    emptyBoxShow: false
  },

  getRoute: function () {
    wx.showLoading({
      title: '生成路线中...'
    })

    loginUtils.checkLogin()
    const tokenObj = wx.getStorageSync('tokenObj')
    // POST请求 将数据发送到后端，并从后端获取生成的旅游路线
    const { destination, travelDays, budget, preferences } = this.data
    wx.request({
      url: 'http://127.0.0.1:8001/route_auto_generate',
      data: {
        id: tokenObj.id,
        destination,
        travelDays,
        budget,
        preferences
      },
      method: 'POST',
      success: (res) => {
        console.log(res)
        wx.hideLoading()
        if (res.statusCode == 200) {
          const { route } = res.data.data
          if (route) {
            this.setData({
              route,
              tip: '已为您生成旅游路线！'
            })
          } else {
            //未能生成旅游路线
            wx.showToast({
              title: '很抱歉，未能为您生成旅游路线！',
              icon: 'none',
            })
          }
          this.setData({
            tipShow: false,
            emptyBoxShow: true
          })
        } else {
          wx.showToast({
            title:'出错了！',
            icon:'error'
          })
          this.setData({
            tipShow: false,
            emptyBoxShow: true
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        if (err.errMsg.includes('timeout')) {
          wx.showToast({
            title: '请求超时,未能生成旅游路线！',
            icon: 'none',
            duration:5000
          })
          this.setData({
            tipShow: false,
            emptyBoxShow: true
          })
        }
      }
    })
  },

  onLoad(options) {
    this.setData({
      token: app.globalData.token,
      destination: decodeURIComponent(options.destination || ''),
      travelDays: decodeURIComponent(options.travelDays || ''),
      budget: decodeURIComponent(options.budget || ''),
      preferences: decodeURIComponent(options.preferences || ''),
      tip: '正在为您生成旅游路线中...',
      route: '',
      tipShow: true,
      emptyBoxShow: false
    })
    this.getRoute()
  },
  onReady() {},
  onShow() {},
  onHide() {},
  onUnload() {},
  onPullDownRefresh() {},
  onReachBottom() {},
  onShareAppMessage() {}
})