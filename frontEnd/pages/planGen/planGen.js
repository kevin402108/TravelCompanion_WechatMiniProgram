// pages/planGen/planGen.js
Page({
  data: {
    questions: [
      {
        id: 1,
        text: "您在选择旅游目的地时，通常更倾向于：",
        type: "single",
        options: [
          "探索未知、寻找独特的旅行体验",
          "选择热门景点、享受热闹氛围",
          "依赖朋友/家人的建议、避免过多选择",
        ],
        category: "personality", //性格
      },
      {
        id: 2,
        text: "您最喜欢的旅游活动是？",
        type: "single",
        options: ["登山徒步","越野冒险","探索历史遗迹","参观名胜古迹", "体验当地习俗文化","品尝美食"],
        category: "preference", //旅游偏好
      },
      {
        id: 3,
        text: "您希望在旅游中享受哪些体验？（至少选一项）",
        type: "multiple",
        options: [
          "徒步探险",
          "沙滩休闲",
          "美食体验",
          "参观博物馆",
          "游玩主题乐园",
        ],
        category: "hobbies", //兴趣爱好
      },
      {
        id: 4,
        text: "您通常更喜欢安排什么样的旅行周期？",
        type: "single",
        options: [
          "短途旅行（1-3天）",
          "中长途旅行（4-7天）",
          "长途旅行（超过7天）",
        ],
        category: "duration", //计划旅行天数
      },
      {
        id: 5,
        text: "您的旅游预算范围是多少？",
        type: "single",
        options: [
          "0-1000元",
          "1000-3000元",
          "3000-5000元",
          "5000-10000元",
          "10000元以上",
        ],
        category: "budget", //预算
      },
    ],
    personality: "",
    preference: "",
    hobbies: "",
    duration: "",
    budget: "",
  },

  handleChoice(e) {
    const questionType = e.currentTarget.dataset.type; //问题所属测评方面
    let value = e.detail.value;
    this.setData({
      [questionType]: value,
    });
    // console.log(questionType + " " + value,this.data[questionType]);
  },

  submitSurvey() {
    //检查是否有未填写的问题
    const { personality, preference, hobbies, duration, budget } = this.data;
    if (!personality || !preference || !hobbies || !duration || !budget) {
      wx.showToast({
        title: "您还有未完成的问题！",
        icon: "none",
        duration: 2500,
      });
      return;
    }

    const queryObj = {
      personality:this.data.personality,
      prefernece:this.data.preference,
      hobbies:this.data.hobbies.join('、'),
      duration:this.data.duration,
      budget:this.data.budget
    }
    const queryStr = Object.keys(queryObj).map(key => `${key}=${encodeURIComponent(queryObj[key])}`).join('&')
    
    wx.redirectTo({
      url: `/pages/planGen/planGenResult/planGenResult?${queryStr}`
    }); 
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {},

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
