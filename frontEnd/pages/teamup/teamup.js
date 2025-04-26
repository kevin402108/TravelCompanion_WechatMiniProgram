import loginUtils from "../../utils/loginUtils";
import userUtils from "../../utils/userUtils";

const app = getApp();

Page({
  data: {
    genderOptions: [
      { id: 1, gender: "男", value: 0 },
      { id: 2, gender: "女", value: 1 },
    ],
    picUrl: "",
    nickname: "",
    gender: "",
    travelDays: 0,
    budget: "",
    partnerList: "",
    tip: "",
    emptyResultText: "",
    showAddPicBox: true,
    hideForm: "",
    msg: "",
    isNicknameValid: "",
  },

  findPartner: function () {
    wx.showLoading({
      title: "寻找旅伴中....",
    });

    /*  wx.request({
      url: "#",
      data: {
        token,
        gender: this.data.gender,
        startDate: this.data.startDate,
        endDate: this.data.endDate,
        budget: this.data.budget,
      },
      method: 'POST',
      success: (res) => {
        console.log(res)
        wx.hideLoading()
        if(res.statusCode == 200){
          const { partnerList } = res.data.data;
          if (partnerList.length > 0) {
            this.setData({
              partnerList: partnerList,
              hideForm: false,
            })
          } else {
            this.setData({
              emptyResultText: "暂无合适的伙伴！",
              hideForm: false,
            })
          }
          this.data.hideForm = false;
        }
      },
      fail: (err) => {
        wx.hideLoading();
        wx.showToast({
          title: "请求超时，请稍后重试！",
          icon: "none",
          duration: 2500,
        })
        this.setData({
          emptyResultText: "暂无合适的伙伴！",
          hideForm: false,
        })
      },
    }) */

    setTimeout(() => {
      wx.hideLoading();
      this.setData({
        partnerList: [
          {
            id: 1,
            picUrl: "https://img-storage-1336210390.cos.ap-guangzhou.myqcloud.com/%E6%97%85%E8%A1%8C.png",
            initator: "kevinchan042108", //组队发起者
            createTime: "2025-1-20 17:45:30", //组队发起时间
            travelDays: 8, //计划旅行天数
            budget: 2000, //组队预算
            preference: "亲近大自然,远离喧嚣,喜欢宁静", //发起者旅游偏好
          },
          {
            id: 2,
            picUrl: "https://img-storage-1336210390.cos.ap-guangzhou.myqcloud.com/%E6%97%85%E6%B8%B8_%E8%B7%AF%E7%BA%BF.png",
            initator: "kevinchan",
            createTime: "2025-1-20 17:45:30",
            travelDays: 8,
            budget: 2000,
            preference: "亲近大自然,远离闹市喧嚣",
          },
        ],
        hideForm: false,
      });
    }, 5000);
  },

  //防抖/节流优化？
  joinTeamup(evt) {
    //流程
    const { id } = evt.target.dataset;
    const { nickname, token } = this.data;
    wx.showLoading({
      title: "正在组队中",
    });

    /* wx.request({
      url: "#",
      method: "PUT",
      data: {
        token,
        id, //组队编号
        participant: nickname, //搭子昵称
      },
      success: (res) => {
        console.log(res)
        wx.hideLoading()
        if (res.statusCode == 200) {
          wx.showToast({
            title: "组队成功！",
          })

          setTimeout(() => {
            wx.switchTab({
              url: "/pages/chatspace/chatspace"
            });
          }, 2000)
        } else {
          wx.hideLoading();
          wx.showToast({
            title: "组队失败！",
            icon: "error"
          })
        }
      },
      fail: (err) => {
        console.log(err);
        wx.hideLoading();
        wx.showToast({
          title: "组队失败！",
          icon: "error"
        })
      },
    }) */

    //组队成功效果
    setTimeout(() => {
      wx.hideLoading();
      wx.showToast({
        title: "组队成功！",
        icon: "success",
        duration: 2000,
      });
      setTimeout(() => {
        wx.switchTab({
          url: "/pages/home/home",
        });
      }, 2000);
    }, 3000);
  },

  //如未选择照片，则上传默认图片
  createTeamup() {
    const { picUrl, nickname, gender, travelDays, budget, preference, token } = this.data;

    if (!nickname) {
      wx.showToast({
        title: '请填写您的昵称！',
        icon: 'none'
      })
      return
    }

    if (!userUtils.checkNickname(nickname)) {
      wx.showToast({
        title: '昵称不符合要求！',
        icon: 'none'
      })
      return
    }

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

    wx.showLoading({
      title: "正在发布中",
    });

    /* wx.request({
      url: "#",
      method: "POST",
      data: {
        token,
        picUrl,
        initator,
        travelDays,
        budget,
        preference,
      },
      success: (res) => {
        console.log(res);
        if (res.statusCode == 200) {
          wx.hideLoading();
          wx.showToast({
            title: "发布成功！",
            icon: "success",
          })
          wx.switchTab({
            url: "/pages/chatspace/chatspace",
          })
        } else {
          wx.hideLoading();
          wx.showToast({
            title: "发布失败！",
            icon: "error"
          })
        }
      },
      fail: (err) => {
        console.log(err);
        wx.hideLoading();
        wx.showToast({
          title: "发布失败！",
          icon: "error",
        })
      },
    }) */

    setTimeout(() => {
      wx.hideLoading();
      wx.showToast({
        title: "发布成功！",
        icon: "success",
        duration: 1000,
      });
      setTimeout(
        () =>
          wx.switchTab({
            url: "/pages/home/home",
          }),
        2000
      );
    }, 3000);
  },

  onpicChoose() {
    const that = this;
    wx.chooseMedia({
      count: 1,
      mediaType: ["image"],
      sourceType: ["album", "camera"],
      sizeType: ["original"],
      success(res) {
        const { tempFilePath } = res.tempFiles[0];

        //上传图片到服务器 待实现 POST请求
        /* wx.uploadFile({
          url:'#',
          filePath:tempFilePath,
          name:'teamup-image-file',
          formData:{token},
          success:(res)=>{
            if(res.statusCode == 200){
              const {imgUrl} = res.data.data
              that.setData({
                picUrl:imgUrl,
                showAddPicBox:false
              })
            } else {
              wx.showToast({
                title:'上传失败！',
                icon:'error'
              })
            }
          },
          fail:(err)=>{
            console.log(err)
            wx.showToast({
                title:'上传失败！',
                icon:'error'
            })
          }
        }) */

        that.setData({
          picUrl: tempFilePath,
          showAddPicBox: false,
        });
      },
      fail(err) {
        console.log(err);
      },
    });
  },

  onnicknameChange: userUtils.onnicknameChange,

  onSliderChange: userUtils.onSliderChange,

  onLoad(options) {
    loginUtils.checkLogin()
    const tokenObj = wx.getStorageSync('tokenObj')
    //通过token获取用户昵称 GET请求
    wx.request({
      url: 'http://127.0.0.1:8001/user/profile',
      data: {
        id:tokenObj.id
      },
      success: (res) => {
        console.log(res);
        wx.hideNavigationBarLoading();
  
        if (res.statusCode == 200) {
          const { nickname,gender } = res.data.data.userInfo;
          this.setData({
            nickname,
            gender
          })
        } else {
          wx.hideNavigationBarLoading();
          wx.showToast({
            title:'获取昵称失败！',
            icon:'none'
          })
        }
      },
      fail: (err) => {
        wx.hideNavigationBarLoading();
        wx.showToast({
          title:'获取昵称失败！',
          icon:'none'
        })
      },
    })
    Object.keys(options).forEach((key) =>
      this.setData({
        [key]: decodeURIComponent(options[key]),
      })
    );
    this.findPartner();
  },
});
