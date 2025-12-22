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
  onchooseAvatar() {
    const that = this
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: function (res) {
        loginUtils.checkLogin()
        const tokenObj = wx.getStorageSync('tokenObj')
        const { id } = tokenObj
        const avatarUrl = res.tempFilePaths[0]
        const image_url = avatarUrl
        console.log(image_url)
        wx.uploadFile({
          url: 'http://127.0.0.1:8001/upload/image',
          filePath: image_url,
          name: 'image_files',
          formData: {
            id: id
          },
          timeout: 5000,
          success:function(res) {
            console.log(res)
            if (res.statusCode == 200) {
              try {
                const data = JSON.parse(res.data)
                const { image_urls } = data.data
                if (image_urls && image_urls.length > 0) {
                  that.setData({
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
            } else if (res.statusCode == 400) {
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
      fail: function () {
        wx.showToast({
          icon:'error',
          title:'图片未选择或图片选择失败',
          duration:5000
        })
      },
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

  //点击保存按钮时 修改服务器对应用户数据（待完善！！！）
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

    const requestData = {
      id:id,
      avatar: avatar || '',
      nickname: nickname || '',
      gender: gender || '',
      hobby: hobby || ''
    }
    console.log('请求数据：', requestData)
    
    //PUT请求
    wx.request({
      url: 'http://127.0.0.1:8001/auth/updateUserInfo',
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      data: requestData,
      success: (res) => {
        console.log('保存响应:', res)
        if (res.statusCode == 200) {
          wx.showToast({
            title: '保存成功!',
            icon: 'success',
          })
          wx.navigateBack({
            url: '/pages/me/me'
          })
        } else if (res.statusCode == 422) {
          // 处理422验证错误
          console.error('验证错误详情:', res.data)
          const errorMsg = '数据格式错误，请检查填写内容'
          if (res.data && res.data.detail) {
          // 解析Pydantic验证错误
            const errorMsg = res.data.detail.map(err => `${err.loc[1]}: ${err.msg}`).join('; ')
          }
          wx.showToast({
            title: errorMsg,
            icon: 'none',
            duration: 3000
          })
        } else {
          const errorMsg = '保存失败！'
          wx.showToast({
            title: errorMsg,
            icon: 'error',
          })
        }
      },
      fail: (err) => {
        console.log('网络错误:', err)
        wx.showToast({
          title: '网络错误，请检查网络连接后重试！',
          icon: 'error',
        })
      }
    })
  },

  //打开时自动获取并填充用户信息
  onLoad(options) {
    wx.showNavigationBarLoading()
    loginUtils.checkLogin()
    const tokenObj = wx.getStorageSync('tokenObj')
    const { id } = tokenObj
    if( !id ) {
      wx.hideNavigationBarLoading()
      wx.showToast({
        title: '无法获取到用户ID！',
        icon: 'none',
      })
      return
    }
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
            avatar: avatar || app.globalData.DEFAULT_AVATAR_URL,
            nickname,
            gender,
            hobby
          })
        } else {
          wx.showToast({
            title: '获取用户信息失败！',
            icon: 'none',
          })
          this.setData({
            avatar: app.globalData.DEFAULT_AVATAR_URL,
          })
        }
      },
      fail: (err) => {
        wx.hideNavigationBarLoading()
        console.log(err)
        wx.showToast({
          title: '请检查网络连接后重试！',
          icon: 'none',
          duration: 2000
        })
        this.setData({
          avatar: app.globalData.DEFAULT_AVATAR_URL,
        })
      },
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