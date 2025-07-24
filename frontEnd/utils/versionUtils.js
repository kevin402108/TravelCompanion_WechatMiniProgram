// 版本兼容性判断及处理工具库
const DEFAULT_VERSION = '1.0.0'
function compareSDKVersion(ver1, ver2) {
    ver1 = ver1.split('.').map(Number);
    ver2 = ver2.split('.').map(Number);
    const len = Math.max(ver1.length, ver2.length);
    for (let i = 0; i < len; i++) {
        const num1 = ver1[i] || 0;
        const num2 = ver2[i] || 0;
        if (num1 !== num2) return num1 > num2 ? 1 : -1;
    }
    return 0;
}

function isSDKVersionSuitable(ver1,ver2) {
    if(typeof ver1 !== 'string' || typeof ver2 !== 'string') return false
    const compareResult = compareSDKVersion(ver1,ver2)
    return compareResult >= 0 ? true : false
}

function getLocalSDKVersion() {
    try {
        const storageVer = wx.getStorageSync('LocalSDKVersion')
        if(storageVer) return storageVer
        else { 
            const SDKVersion = wx.getSystemInfoSync().SDKVersion ?? DEFAULT_VERSION
            wx.setStorageSync('LocalSDKVersion', SDKVersion)
            return SDKVersion
        } 
    } catch(e) {
        console.error('缓存操作失败!', e)
        return DEFAULT_VERSION
    }
}

export default {
    compareSDKVersion,
    isSDKVersionSuitable,
    getLocalSDKVersion
}