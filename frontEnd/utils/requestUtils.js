import loginUtils from "./loginUtils";
import {writeLog} from "./loggerUtils";
const app = getApp()
const sitePrefix = "http://43.138.103.184:8001"

/**
 * 带token验证的请求模板
 * @param {String} url 请求地址
 * @param {Object} options 请求参数
 * @return {Promise}
 **/
const requestWithAuth = (url, options={}) => {
    // console.log(isNeedGetTokenobj())
    if (isNeedGetTokenobj()) {
        writeLog('requestWithAuth','WARNING','Local Storage中的tokenobj无效，需要重新获取')
        setTimeout(()=>{
            loginUtils.checkLogin(app);
        },1000)
        loginUtils.checkLogin(app);
        if(isNeedGetTokenobj()) {
            writeLog('requestWithAuth','ERROR','Local Storage中的tokenobj仍然无效，弹登录选择模态框给用户')
            return Promise.reject(new Error('Authentication required!'));
        }
    }

    const tokenObj = wx.getStorageSync('tokenObj');
    const token = tokenObj?.token;

    url = `${sitePrefix}${url}`;
    const requestOptions = {
        url: url,
        header: {
            Authorization: `Bearer ${token}`,
            'content-type': 'application/json'
        },
        data:{
            ...options.data,
        },
        ...Object.fromEntries(
            Object.entries(options).filter(([key]) => key !== 'data')
        )
    }

    return new Promise((resolve, reject)=>{
        wx.request({
            ...requestOptions,
            success: (res) => resolve(res),
            fail: (err) => reject(err)
        });
    });
}

/**
 * 判断是否需要获取tokenObj
 * @return {Boolean}
 **/
const isNeedGetTokenobj = ()=>{
    const tokenObj = wx.getStorageSync('tokenObj');
    if(!tokenObj) return true;
    
    const {token,isNewUser,token_expired_at} = tokenObj;
    if(isNewUser || typeof isNewUser !== 'boolean') return true;
    if(!loginUtils.isValidToken(token)) return true;

    const now = Math.floor(Date.now() / 1000);
    if(!token_expired_at || typeof token_expired_at !== 'number' || token_expired_at <= now) return true;
    return false;
}

/**
 * 显示登录指引模态框
 **/
const showLoginGuideModal = ()=>{
    wx.showModal({
        title: '温馨提示',
        content: '用户认证失败，请先登录！',
        showCancel: true,
        cancelText: '取消',
        confirmText: '登录小程序',
        success:(res)=>{
            if(res.confirm) {
                writeLog('showLoginGuideModal','INFO','用户选择登录，将重新执行checkLogin流程')
                loginUtils.checkLogin(app);
            }
            else {
                app.setLoginStatus(false);
                writeLog('showLoginGuideModal','WARNING','用户选择不登录，将无法使用部分功能，并跳转小程序首页')
                wx.showToast({
                    title: '稍后将自动返回首页',
                    icon: 'none',
                    duration: 2000
                })
                setTimeout(()=>{
                    wx.switchTab({
                        url:'/pages/home/home'
                    })
                },2000)
            }
        },
        fail:(err)=>{
            app.setLoginStatus(false);
            writeLog('showLoginGuideModal','ERROR','模态框加载失败！')
            wx.showToast({
                title: '用户认证出错，请稍后再试!',
                icon: 'none',
                duration: 2000
            })
        }
    })
}

export default {
    sitePrefix,
    requestWithAuth,
    isNeedGetTokenobj,
    showLoginGuideModal
}
