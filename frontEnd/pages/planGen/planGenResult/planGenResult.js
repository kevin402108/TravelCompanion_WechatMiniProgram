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
    plan: "",
    tipShow: true, //是否显示顶部的tip区域和分割线
    emptyBoxShow: false, //是否展示生成失败的样式
  },

  getTravelPlan: function () {
  wx.showLoading({
    title: "正在生成中...",
  });

  loginUtils.checkLogin(); // 确保用户已登录
  const { personality, hobbies, budget, preferences, duration } = this.data;

  // 使用 requestUtils 发起带认证的请求
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
            tip: "已为您生成以下旅游方案",
            plan: res.data.data.plan,
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

  onReady() {},
  onShow() {},
  onHide() {},
  onUnload() {},
  onPullDownRefresh() {},
  onReachBottom() {},
  onShareAppMessage() {}
});
