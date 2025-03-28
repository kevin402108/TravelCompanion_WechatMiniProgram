import userUtils from '../../../utils/userUtils'
import loginUtils from '../../../utils/loginUtils'
const app = getApp()
const _ = require('lodash')

Page({
  data: {
    id: '',
    token: '',
    genderArr: ['男', '女', '暂不选择'],
    genderIndex: 0,
    avatar: '',
    nickname: '',
    gender: '',
    hobby: '',
    isNicknameValid: '', //昵称是否符合规范
    msg: ''
  },

  //选择图片，上传服务器，返回的生成网络图片地址 POST请求（待完善）
  onchooseAvatar(evt) {
    console.log(evt)
    const { avatarUrl } = evt.detail
    console.log(avatarUrl)

    if (!avatarUrl) {
      wx.showToast({
        title: '未选择图片！',
        icon: 'error',
        duration: 2000
      })
      return
    }

    loginUtils.checkLogin()
    const tokenObj = wx.getStorageSync('tokenObj')
    const { id } = tokenObj

    const image_url = avatarUrl
    wx.uploadFile({
      url: 'http://127.0.0.1:8001/upload/image',
      filePath: image_url,
      name: 'image-files',
      formData: {
        id: id
      },
      timeout: 5000,
      success: (res) => {
        console.log(res)
        if (res.statusCode == 200) {
          try {
            const data = JSON.parse(res.data)
            const { image_urls } = data.data
            if (image_urls && image_urls.length > 0) {
              this.setData({
                avatar: image_urls
              })
            } else {
              console.log('返回数据格式异常！')
              wx.showToast({
                title: '服务器返回数据异常！',
                icon: 'error',
                duration: 2000
              })
            }
          } catch (err) {
            console.log(err)
            wx.showToast({
              title: '服务器返回数据异常！',
              icon: 'error',
              duration: 2000
            })
          }
        } else if(res.statusCode == 400) {
          wx.showToast({
            title: '请求参数错误！',
            icon: 'error',
            duration: 2000
          }) 
        } else if (res.statusCode == 401) {
          console.log('用户不存在！')
        } else if (res.statusCode === 500) {
          wx.showToast({
            title: '服务器内部错误！',
            icon: 'error',
            duration: 2000
          })
        } else {
          wx.showToast({
            title: '未知错误！',
            icon: 'error',
            duration: 2000
          })
        }
      },
      fail: (err) => {
        console.log(err)
        wx.showToast({
          title: '更换头像失败！',
          icon: 'error',
          duration: 2000
        })
      }
    })
  },

  onnicknameChange: userUtils.onnicknameChange,

  ongenderChange(evt) {
    const { genderArr } = this.data
    const genderIndex = evt.detail.value
    if (genderIndex == 2) {
      this.setData({
        genderIndex: '',
        gender: ''
      })
      return
    }
    const gender = genderArr[genderIndex]
    this.setData({
      genderIndex,
      gender
    })
  },

  //点击保存按钮时 修改服务器对应用户数据（待完善）
  saveInfo() {

    const { avatar, nickname, gender, hobby } = this.data
    if (nickname && !userUtils.checkNickname(nickname)) {
      wx.showToast({
        title: '昵称不符合要求！',
        icon: 'none',
        duration: 2000
      })
      return
    }

    loginUtils.checkLogin()
    const tokenObj = wx.getStorageSync('tokenObj')
    const { id } = tokenObj

    //PUT请求
    wx.request({
      url: 'http://127.0.0.1:8001/auth/updateUserInfo',
      method: 'PUT',
      data: {
        id,
        avatar,
        nickname,
        gender,
        hobby
      },
      success: (res) => {
        console.log(res)
        if (res.statusCode == 200) {
          wx.showToast({
            title: '保存成功!',
            icon:'success',
            duration:2500
          })
          wx.navigateBack({
            url: '/pages/me/me'
          })
        } else {
          wx.showToast({
            title: '保存失败！',
            icon: 'error',
            duration: 2000
          })
        }
      },
      fail: (err) => {
        console.log(err)
        wx.showToast({
          title: '保存失败！',
          icon: 'error',
          duration: 2000
        })
      }
    })

    // wx.showToast({
    //   title: '保存成功',
    //   icon: 'success',
    //   duration: 2000
    // })
    // setTimeout(() => {
    //   wx.navigateBack({
    //     url: '/pages/me/me'
    //   })
    // }, 2000)
  },

  //打开时自动获取并填充用户信息（待完善）
  onLoad(options) {
    wx.showNavigationBarLoading()
    const tokenObj = wx.getStorageSync('tokenObj')
    // console.log(tokenObj)
    if (!tokenObj) return
    const {id} = tokenObj

    // GET请求
    wx.request({
      url: `http://127.0.0.1:8001/user/profile`,
      data: {
        id
      },
      timeout: 5000,
      success: (res) => {
        console.log(res)
        wx.hideNavigationBarLoading()
        if (res.statusCode == 200) {
          const { userInfo } = res.data.data
          const { avatar, nickname, gender, hobby } = userInfo
          this.setData({
            avatar: avatar || app.globalData.defaultAvatarUrl,
            nickname,
            gender,
            hobby
          })
        } else {
          wx.showToast({
            title: '获取用户信息失败！',
            icon: 'none',
            duration: 2000
          })
          this.setData({
            avatar: app.globalData.defaultAvatarUrl,
          })
        }
      },
      fail: (err) => {
        wx.hideNavigationBarLoading()
        console.log(err)
        wx.showToast({
          title: '获取用户信息失败！',
          icon: 'none',
          duration: 2000
        })
        this.setData({
          avatar: app.globalData.defaultAvatarUrl,
        })
      },
    })
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  }
})