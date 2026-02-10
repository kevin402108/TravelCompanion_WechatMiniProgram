import loginUtils from "../../../utils/loginUtils"
import requestUtils from "../../../utils/requestUtils";

const app = getApp();
Page({
  data: {
    tip: "",
    personality: "",
    hobbies: "",
    budget: "",
    preferences: "",
    duration: "",
    plan: null,
    tipShow: true,
    emptyBoxShow: false
  },

  onLoad(options) {
    this.setData({
      token: app.globalData.token,
      personality: decodeURIComponent(options.personality || ""),
      preferences: decodeURIComponent(options.preferences || ""),
      hobbies: decodeURIComponent(options.hobbies || ""),
      duration: decodeURIComponent(options.duration || ""),
      budget: decodeURIComponent(options.budget || ""),
      plan: "",
      tip: "正在为您生成个性化的旅游方案！",
      warningText: "",
      tipShow: true,
      emptyBoxShow: false,
    });
    this.getTravelPlan();
  },

  navigateToAIPlan() {
    wx.switchTab({
      url: '/pages/ai-chat/ai-chat',
    });
  },

  navigateToHistory() {
    wx.navigateTo({
      url: '/pages/historyPlan/historyPlan'
    });
  },

  getTravelPlan: function () {
  wx.showLoading({
    title: "正在生成中...",
  });

  const { personality, hobbies, budget, preferences, duration } = this.data;
  requestUtils.requestWithAuth("/travelPlans", {
      method: "POST",
      data: {
        personality,
        hobbies,
        budget,
        duration,
        preferences,
      },
    }).then((res) => {
      wx.hideLoading();
      console.log(res);

      if (res.statusCode === 200) {
        const { plan } = res.data.data;
        if (plan) {
            this.setData({
              plan: {
                budget: res.data.data.plan.budget,
                arrange: res.data.data.plan.arrange || []
              },
              tip: "已为您生成以下个性化旅游方案",
              tipShow: false,
              emptyBoxShow: true
            });
        } else {
          wx.showToast({
            title: "很抱歉，未能为您生成旅游方案！",
            icon: "none",
          });
          this.setData({
            tip: "",
            tipShow: false,
            emptyBoxShow: true,
          });
        }
      }
    }).catch((err) => {
      wx.hideLoading();
      wx.showToast({
        title: "出错了,未能为您生成旅游方案！",
        icon: "none",
      });
      this.setData({
        tip: "",
        tipShow: false,
        emptyBoxShow: true,
      });
    });
  },

  onReady() {},
  onShow() {},
  onHide() {},
  onUnload() {},
  onPullDownRefresh() {},
  onReachBottom() {},
  onShareAppMessage() {}
});
