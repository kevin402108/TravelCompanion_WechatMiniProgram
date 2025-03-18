const _ = require('lodash')

// 检测用户昵称
const checkNickname = (nickname) => {
    if (!nickname) return true
    const reg = /^[a-zA-Z0-9\u4e00-\u9fa5_]+$/
    return reg.test(nickname)
}

//检测当前输入的昵称是否符合要求 （已防抖优化）
function onnicknameChange(evt) {
    const nickname = evt.detail.value
    if (!nickname) {
        return this.setData({
            isNicknameValid: '',
            msg: ''
        })
    }
    const getValidResult = _.debounce((nickname) => {
        const isNicknameValid = checkNickname(nickname)
        this.setData({
            isNicknameValid,
            msg: isNicknameValid ? '昵称可用!' : '昵称只能含有大小写字母、0-9、下划线和中文字符!'
        })
    }, 500)
    getValidResult(nickname)
}

//处理所选单选框变化时性别的变化
function onGenderChange(e) {
    const gender = e.detail.value
    this.setData({
        gender
    })
}

//针对slider滑块变动的处理函数，id为滑块value所绑定的data项
function onSliderChange(e) {
    const typeId = e.target.id || ''
    if (typeId) {
        this.setData({
            [typeId]: e.detail.value
        })
    }
}

const isSepeicalProvince = (province)=> {
    return province == '北京市' || province == '天津市' || province == '上海市' || province == '重庆市' || province == '香港特别行政区' || province == '澳门特别行政区'
}

export default {
    checkNickname,
    onnicknameChange,
    onGenderChange,
    onSliderChange,
    isSepeicalProvince,
}