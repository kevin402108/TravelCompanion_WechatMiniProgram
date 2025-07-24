import versionUtils from './versionUtils'

function isComponentUsable(schema,minVersion){
    const SDKVersion = versionUtils.getLocalSDKVersion()
    if(typeof wx.canIUse === 'function') {
        return wx.canIUse(schema)
    }
    return versionUtils.isSDKVersionSuitable(SDKVersion,minVersion)
}

function isAPISupported(minRequiredVer) {
    try {
        const curSDKVer = versionUtils.getLocalSDKVersion()
        return versionUtils.isSDKVersionSuitable(curSDKVer,minRequiredVer) 
    } catch(e) {
        console.error('API兼容检查失败:', e)
        return false
    }
}

export default {
    isAPISupported,
    isComponentUsable
}


