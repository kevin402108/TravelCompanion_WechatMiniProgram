import loginUtils from '../../../utils/loginUtils'
import requestUtils from "../../../utils/requestUtils";
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
    });

    // 使用 requestWithAuth 进行带 token 验证的请求
    const { destination, travelDays, budget, preferences } = this.data;
    requestUtils.requestWithAuth('/routes/auto_generate', {
      method: 'POST',
      data: {
        destination,
        travelDays,
        budget,
        preferences
      }
    }).then((res) => {
      wx.hideLoading();
      if (res.statusCode === 200) {
        const { route } = res.data.data;
        if (route) {
          this.setData({
            route,
            tip: '已为您生成旅游路线！'
          });
        } else {
          wx.showToast({
            title: '很抱歉，未能为您生成旅游路线！',
            icon: 'none'
          });
        }
        this.setData({
          tipShow: false,
          emptyBoxShow: true
        });
      } else {
        wx.showToast({
          title: '出错了！',
          icon: 'error'
        });
        this.setData({
          tipShow: false,
          emptyBoxShow: true
        });
      }
    }).catch((err) => {
      wx.hideLoading();
      if (err.errMsg && err.errMsg.includes('timeout')) {
        wx.showToast({
          title: '请求超时,未能生成旅游路线！',
          icon: 'none',
          duration: 5000
        });
      } else {
        wx.showToast({
          title: '网络错误，请稍后再试！',
          icon: 'none'
        });
      }
      this.setData({
        tipShow: false,
        emptyBoxShow: true
      });
    });
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