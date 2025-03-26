import userUtils from "../../../utils/userUtils";

// pages/teamup/teamup.js
Page({
  data: {
    genderOptions: [
      { id: 1, gender: "男"},
      { id: 2, gender: "女"},
    ],
    gender: "",
    travelDays:0,
    budget: 0,
    preference: "",
    isDisabled:"",
  },

  handleChoice: userUtils.onGenderChange,

  //多个滑块共用此函数，用所点击滑块的id来区别设置的数据项
  onSliderChange:userUtils.onSliderChange,

  submitForm() {
    const {gender,travelDays,budget,preference} = this.data
    if (!gender) {
      wx.showToast({
        title: '请选择您的性别！',
        icon: 'none'
      })
      return
    }

    if (!travelDays) {
      wx.showToast({
        title: '请填写您的旅游天数！',
        icon: 'none'
      })
      return
    }

    if (!preference) {
      wx.showToast({
        title: '请填写您的旅游偏好！',
        icon: 'none'
      })
      return
    }

    const queryObj = {
      gender,
      travelDays,
      budget,
      preference
    }
    const queryStr = Object.keys(queryObj).map(key => `${key}=${encodeURIComponent(queryObj[key])}`).join('&')
    wx.redirectTo({
      url:`/pages/teamup/teamup?${queryStr}`
    })
  },

  resetForm() {
    this.setData({
      gender: "",
      travelDays:0,
      budget: 0,
      preference: ""
    })
  },

  //生命周期函数--监听页面加载
  onLoad(options) {
    //通过token获取用户昵称和性别 GET请求
    /* const token = ''
    wx.request({
      url: "#",
      data: {
        token,
      },
      timeout: 5000,
      success: (res) => {
        console.log(res);
        wx.hideNavigationBarLoading();
        if (res.statusCode == 200) {
          const { gender } = res.data.data.userInfo;
          this.setData({
            gender
          })
        } else {
          wx.hideNavigationBarLoading();
          wx.showToast({
            title:'获取用户信息失败！',
            icon:'none'
          })
        }
      },
      fail: (err) => {
        wx.hideNavigationBarLoading();
        wx.showToast({
          title:'获取用户信息失败！',
          icon:'none'
        })
      },
      complete:() => {
        const gender = this.data.gender
        this.setData({
          isDisabled:gender ? true : false
        })
      }
    }) */
   const gender = ''
    this.setData({
      gender,
      travelDays:0,
      budget: 0,
      isDisabled:gender ? true : false
    });
  },

  //生命周期函数--监听页面初次渲染完成
  onReady() {},

  //生命周期函数--监听页面显示
  onShow() {},

  //生命周期函数--监听页面隐藏
  onHide() {},

  //生命周期函数--监听页面卸载
  onUnload() {},

  //页面相关事件处理函数--监听用户下拉动作
  onPullDownRefresh() {},

  //页面上拉触底事件的处理函数
  onReachBottom() {},

  //用户点击右上角分享
  onShareAppMessage() {},
});
