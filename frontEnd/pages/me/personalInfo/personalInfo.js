import userUtils from '../../../utils/userUtils'
import loginUtils from '../../../utils/loginUtils'
import requestUtils from "../../../utils/requestUtils";
import {writeLog} from "../../../utils/loggerUtils";
const app = getApp()
const _ = require('lodash')

Page({
  data: {
    genderArr: ['男', '女', '暂不选择'],
    genderIndex: 0,
    avatar: '',
    nickname: '',
    gender: '',
    hobby: '',
    isNicknameValid: '', //昵称是否符合规范
    msg: ''
  },

  onnicknameChange: userUtils.onnicknameChange,

  ongenderChange(evt) {
    const { genderArr } = this.data
    const genderIndex = evt.detail.value
    if (genderIndex === 2) {
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

  //保存修改后的用户信息
  saveInfo() {
    const { avatar, nickname, gender, hobby } = this.data;

    if (nickname && !userUtils.checkNickname(nickname)) {
      wx.showToast({
        title: '昵称不符合要求！',
        icon: 'none',
        duration: 2000
      });
      return;
    }

    const requestData = {
      avatar: avatar || '',
      nickname: nickname || '',
      gender: gender || '',
      hobby: hobby || ''
    };

    // PUT请求
    requestUtils.requestWithAuth('/users/me', {
      method: 'PUT',
      data: requestData,
      timeout: 5000
    }).then((res) => {
        console.log('保存响应:', res);
        if (res.statusCode === 200) {
          wx.showToast({
            title: '保存成功!',
            icon: 'success'
          });
          wx.navigateTo({
            url: '/pages/me/me?refresh=true'
          });
        } else if (res.statusCode === 422) {
          console.error('验证错误详情:', res.data);
          const errorMsg = res.data?.detail
            ? res.data.detail.map(err => `${err.loc[1]}: ${err.msg}`).join('; ')
            : '数据格式错误，请检查填写内容';
          wx.showToast({
            title: errorMsg,
            icon: 'none',
            duration: 3000
          });
        } else {
          wx.showToast({
            title: '保存失败！',
            icon: 'error'
          });
        }
      }).catch((err) => {
        console.log('网络错误:', err);
        if (err.message && err.message.includes('Authentication required')) {
          writeLog('个人信息编辑', 'ERROR', '保存用户信息失败 - 需要用户登录');
          requestUtils.showLoginGuideModal();
        } else {
          wx.showToast({
            title: '网络错误，请检查网络连接后重试！',
            icon: 'none'
          });
        }
      });
  },

  //打开时自动获取并填充用户信息
  onLoad(options) {
    wx.showLoading({
      title: '加载中...',
      mask: true
    });
    requestUtils.requestWithAuth('/users/profile', {
      method: "GET",
      timeout: 5000,
    }).then((res) => {
      console.log(res)
      wx.hideLoading();
      if (res.statusCode >= 200 && res.statusCode < 300) {
        const {nickname, avatar, gender, hobby} = res.data.data.userInfo;
        this.setData({
            avatar: avatar || app.globalData.DEFAULT_AVATAR_URL,
            nickname: nickname || '',
            gender: gender || '',
            hobby: hobby || ''
        });
        writeLog('个人信息编辑', 'INFO', '获取用户信息成功!')
      } else {
        if (res.statusCode === 401) {
          writeLog('个人信息编辑', 'ERROR', '获取用户信息失败 - 用户认证失败，token无效或已过期')
          wx.showToast({
            title: "登录已过期，正在重新登录",
            icon: 'none',
            duration: 2000,
          });
          loginUtils.checkLogin(app);
        } else {
          writeLog('个人信息编辑', 'ERROR', `获取用户信息失败 - 错误状态码:${res.statusCode},错误详情：${res.data}`)
          wx.showToast({
            title: "获取用户信息时出错,请稍后重试！",
            icon: 'none',
            duration: 2000
          });
        }
      }
    }).catch((err) => {
      wx.hideLoading();
      if (err.errMsg) {
        writeLog('个人信息编辑', 'ERROR', `获取用户信息失败 - 错误信息:${err.errMsg}`)
        wx.showToast({
          title: "网络错误，请检查网络连接后重试！",
          icon: 'none',
          duration: 2000,
        });
      } else if (err.message && err.message.includes('Authentication required')) {
        writeLog('个人中心', 'ERROR', `获取用户信息失败 - 需要用户登录`)
        return requestUtils.showLoginGuideModal();
      } else {
        console.error('获取用户信息时发生错误:', err);
        wx.showToast({
          title: "获取用户信息失败，请稍后再试！",
          icon: 'none',
          duration: 2000
        });
      }

      this.setData({
          nickname: '',
          avatar: app.globalData.DEFAULT_AVATAR_URL,
          gender: '',
          hobby: ''
      });
    })
  },

  //选择图片，上传服务器，返回的生成网络图片地址 POST请求（待完善）
  // onchooseAvatar() {
  //   const app = getApp()
  //   const that = this
  //   wx.chooseMedia({
  //     count: 1,
  //     mediaType: ['image'],
  //     sourceType: ['album', 'camera'],
  //     sizeType: ['original', 'compressed'],
  //     camera: ['front', 'back'],
  //     success: (res) => {
  //       console.log('选择图片成功:', res)
  //       writeLog('个人信息编辑', 'INFO', '选择头像图片成功')
  //       const tmpAvatarURL = res.tempFiles[0].tempFilePath;
  //       const fileSize = res.tempFiles[0].size;
  //       const fileExtension = tmpAvatarURL.substring(tmpAvatarURL.lastIndexOf('.') + 1).toLowerCase();
  //
  //       const maxSize = 1024 * 1024 * 5;
  //       const validExtensions = ['jpg', 'jpeg', 'png', 'webp'];
  //       if (fileSize > maxSize) {
  //         wx.showToast({
  //           title: '图片大小不能超过5MB!',
  //           icon: 'none'
  //         });
  //         return;
  //       }
  //       if (!validExtensions.includes(fileExtension)) {
  //         wx.showToast({
  //           title: `不支持${fileExtension}格式的图片！`,
  //           icon: 'none'
  //         });
  //         return;
  //       }
  //
  //       that.setData({
  //         avatar: tmpAvatarURL
  //       });
  //       that.uploadImage(tmpAvatarURL)
  //     },
  //     fail: (err) => {
  //       console.log('选择图片失败:', err)
  //       writeLog('个人信息编辑', 'ERROR', `选择头像图片失败: ${JSON.stringify(err)}`)
  //     }
  //   })
  // },

  // uploadImage(tmpPhotoURL) {
  //   const that = this;
  //   if(requestUtils.isNeedGetTokenobj()){
  //     writeLog('uploadImage','WARNING','Local Storage中的tokenobj无效，需要重新获取')
  //     setTimeout(()=>{
  //       loginUtils.checkLogin(app);
  //     },1000)
  //     if(requestUtils.isNeedGetTokenobj()) {
  //       writeLog('uploadImage','ERROR','Local Storage中的tokenobj仍无效，弹登录选择模态框给用户')
  //       return requestUtils.showLoginGuideModal();
  //     }
  //   }
  //
  //   const tokenobj = wx.getStorageSync('tokenObj')
  //   const token = tokenobj?.token
  //
  //   if(!token){
  //     writeLog('uploadImage','ERROR','token为空，请检查token是否正确获取')
  //     return wx.showToast({
  //       title:'登录凭证无效，请稍后再试！',
  //       icon: 'error',
  //       duration: 2000
  //     })
  //   }
  //
  //   wx.showLoading({
  //     title: '上传中...',
  //     mask: true
  //   });
  //
  //   wx.uploadFile({
  //     url:'http://127.0.0.1:8001/upload/image',
  //     filePath: tmpPhotoURL,
  //     name:'user-avatar-image',
  //     header:{
  //       'Authorization': `Bearer ${token}`,
  //       'Content-Type': 'multipart/form-data'
  //     },
  //     formData:{},
  //     timeout:5000,
  //     enableHttp2: true,
  //     success: (res) => {
  //       wx.hideLoading();
  //       console.log(res);
  //       if(res.statusCode >= 200 && res.statusCode < 300){
  //         try {
  //           let data
  //           if(typeof res.data === 'string') data = JSON.parse(res.data)
  //           else data = res.data
  //
  //           if(data.success){
  //             that.setData({
  //               avatar: data.data.url||app.globalData.DEFAULT_AVATAR_URL
  //             })
  //             writeLog('uploadImage', 'INFO', `头像上传成功: ${data.data.url}`)
  //             wx.showToast({
  //               title: '更新头像成功!',
  //               icon: 'success'
  //             });
  //           } else {
  //             writeLog('uploadImage', 'ERROR', `上传失败: ${data.message || '未知错误'}`)
  //             wx.showToast({
  //               title: '头像更新失败，请重试！',
  //               icon: 'none',
  //               duration: 2000
  //             });
  //           }
  //         } catch (parseError) {
  //           writeLog('uploadImage', 'ERROR', `解析响应数据失败: ${parseError.message}`)
  //           console.error('解析响应数据失败:', parseError)
  //           wx.showToast({
  //             title: '头像更新失败，请重试！',
  //             icon: 'none',
  //             duration: 2000
  //           });
  //         }
  //       } else {
  //         if(res.statusCode === 401){
  //           writeLog('uploadImage', 'ERROR', '认证失败，token可能已过期')
  //           wx.showToast({
  //             title:'登录凭证无效，请认证后再试！',
  //             icon: 'none',
  //             duration: 2000
  //           });
  //           loginUtils.checkLogin(app);
  //         } else if (res.statusCode === 400) {
  //           writeLog('uploadImage', 'ERROR', `上传请求参数错误: ${res.data}`)
  //           wx.showToast({
  //             title: '图片格式不支持，请选择其他图片！',
  //             icon: 'none',
  //             duration: 2000
  //           });
  //         } else {
  //           writeLog('uploadImage', 'ERROR', `上传图片失败，HTTP状态码: ${res.statusCode},错误信息:${JSON.stringify(res.data)}`)
  //           wx.showToast({
  //             title: '头像更新失败，请稍后再试',
  //             icon: 'none',
  //             duration: 2000
  //           });
  //         }
  //       }
  //     },
  //     fail:(err)=>{
  //       wx.hideLoading();
  //       console.log('上传图片失败:', err)
  //       if(err.errMsg && err.errMsg.includes('timeout')){
  //         writeLog('uploadImage', 'ERROR', `上传图片失败 - 超时: ${err.errMsg}`)
  //         wx.showToast({
  //           title: '网络连接超时，请稍后重试',
  //           icon: 'none',
  //           duration: 2000
  //         });
  //       } else if(err.errMsg && err.errMsg.includes('abort')){
  //         writeLog('uploadImage', 'ERROR', `上传图片中断 - 用户取消上传: ${err.errMsg}`)
  //         wx.showToast({
  //           title: '头像更新已取消',
  //           icon: 'none',
  //           duration: 2000
  //         });
  //       } else if(err.errMsg && err.errMsg.includes('fail')){
  //         writeLog('uploadImage', 'ERROR', `上传图片失败 - 网络错误: ${err.errMsg}`)
  //         wx.showToast({
  //           title: '网络错误，请稍后重试',
  //           icon: 'none',
  //           duration: 2000
  //         });
  //       } else {
  //         writeLog('uploadImage', 'ERROR', `上传图片失败 - 其他错误: ${JSON.stringify(err)}`)
  //         wx.showToast({
  //           title: '头像更新失败，请稍后再试',
  //           icon: 'error',
  //           duration: 2000
  //         });
  //       }
  //     }
  //   });
  // },

  onReady() {},
  onShow() {},
  onHide() {},
  onUnload() {},
  onPullDownRefresh() {},
  onReachBottom() {},
  onShareAppMessage() {}
})