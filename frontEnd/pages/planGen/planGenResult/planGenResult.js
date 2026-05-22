import { set } from "lodash";
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
    wx.navigateTo({
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
  // requestUtils.requestWithAuth("/travelPlans", {
  //     method: "POST",
  //     data: {
  //       personality,
  //       hobbies,
  //       budget,
  //       duration,
  //       preferences,
  //     },
  //   }).then((res) => {
  //     wx.hideLoading();
  //     console.log(res);

  //     if (res.statusCode === 200) {
  //       const { plan } = res.data.data;
  //       if (plan) {
  //           this.setData({
  //             plan: {
  //               budget: res.data.data.plan.budget,
  //               arrange: res.data.data.plan.arrange || []
  //             },
  //             tip: "已为您生成以下个性化旅游方案",
  //             tipShow: false,
  //             emptyBoxShow: true
  //           });
  //       } else {
  //         wx.showToast({
  //           title: "很抱歉，未能为您生成旅游方案！",
  //           icon: "none",
  //         });
  //         this.setData({
  //           tip: "",
  //           tipShow: false,
  //           emptyBoxShow: true,
  //         });
  //       }
  //     }
  //   }).catch((err) => {
  //     wx.hideLoading();
  //     wx.showToast({
  //       title: "出错了,未能为您生成旅游方案！",
  //       icon: "none",
  //     });
  //     this.setData({
  //       tip: "",
  //       tipShow: false,
  //       emptyBoxShow: true,
  //     });
  //   });
  setTimeout(() => {
    wx.hideLoading();
    this.setData({
      plan: {
        budget: 1500,
        arrange: [
            {
                "title": "第一天：阳朔 & 自由探险",
                "detail":"从桂林出发，乘车前往阳朔（车程约1.5-2小时）。到达后入住民宿，稍作休息。下午开始十里画廊徒步，途经月亮山、剑峰山等景点，步行约4小时。晚上回到民宿，享受当地特色晚餐，体验阳朔的小镇氛围。",
            },
            {
                "title": "第二天：遇龙河漂流 & 探险",
                "detail":"早晨参加遇龙河竹筏漂流（漂流时间约2小时），欣赏沿途的自然山水。下午进行阳朔附近山洞探险，探索当地的溶洞和峡谷。晚上返回阳朔，享受晚餐并放松。",
            },
            {
                "title": "第三天：漓江徒步 & 返回",
                "detail":"早晨前往漓江边进行徒步，沿着漓江走，欣赏山水画般的景色。沿途经过一些宁静的村庄，适合拍照和放松。中午可以在当地的小镇上享用午餐，下午乘车返回,结束行程。",
            },
        ]
      },
      tip: "已为您生成以下个性化旅游方案",
      tipShow: false,
      emptyBoxShow: true
    });
   },4000);
  },

  onReady() {},
  onShow() {},
  onHide() {},
  onUnload() {},
  onPullDownRefresh() {},
  onReachBottom() {},
  onShareAppMessage() {}
});
