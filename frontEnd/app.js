import './utils/lodash-fix'
import versionUtils from './utils/versionUtils'
import {writeLog} from "./utils/loggerUtils";

App({
    globalData: {
        LocalSDKVersion: null,
        MIN_SDK_VERSION: '3.2.5',
        PRIVACY_CONTRACT_NAME: '旅伴奇遇工坊隐私保护指引',
        DEFAULT_AVATAR_URL: "https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0",
        isSuitableVersion: false,
        resolvePrivacy: null,
        isUserLogin: false,
        isPrivacyContractAgreed: false,  // 隐私协议同意状态
        hasShownPrivacyDialog: false  // 是否已显示过隐私弹窗
    },

    getLoginStatus: function(){
        return this.globalData.isUserLogin
    },

    setLoginStatus: function(status){
        this.globalData.isUserLogin = status
        writeLog('auth', 'INFO', `用户全局登录状态已更新为${status}`);
    },

    getPrivacyContractAgreedStatus: function(){
        return this.globalData.isPrivacyContractAgreed
    },

    setPrivacyContractAgreedStatus: function(isPrivacyContractAgreed){
        this.globalData.isPrivacyContractAgreed = isPrivacyContractAgreed
        writeLog('auth', 'INFO', `用户同意隐私协议状态已更新为${isPrivacyContractAgreed}`);
    },

    getPrivacyDialogShownStatus: function(){
        return this.globalData.hasShownPrivacyDialog
    },

    setPrivacyDialogShownStatus: function(status){
        this.globalData.hasShownPrivacyDialog = status
        writeLog('auth', 'INFO', `向用户展示隐私弹窗状态已更新为${status}`);
    },

    getLocalSDKVersion() {
        return this.globalData.LocalSDKVersion
    },

    setLocalSDKVersion(localSDKVersion) {
        this.globalData.LocalSDKVersion = localSDKVersion
        writeLog('app', 'INFO', '全局SDK版本设置完成: ' + localSDKVersion);
    },

    onLaunch: function () {
        this.initializeApp();
    },

    initializeApp() {
        writeLog('app', 'INFO', '小程序开始启动');
        this.initializeSDKVersion();
        this.initializeLoginStatus();
        this.initializePrivacyStatus();
        writeLog('app', 'INFO', '小程序启动完成');
    },

    // 初始化SDK版本
    initializeSDKVersion() {
        const LocalSDKVer = versionUtils.getLocalSDKVersion();
        this.setLocalSDKVersion(LocalSDKVer);
        writeLog('app', 'INFO', 'SDK版本初始化完成: ' + LocalSDKVer);
    },

    // 初始化登录状态
    initializeLoginStatus() {
        // TODO: 获取用户登录状态，更新全局变量,完善登录状态管理
        this.globalData.isUserLogin = false;
        writeLog('auth', 'INFO', '登录状态初始化完成');
    },

    // 初始化用户隐私协议状态
    initializePrivacyStatus() {
        const storedPrivacyAgreedStatus = this.getStorageSafe('is_privacy_agreed', false);
        const storedShownPrivacyDialogStatus = this.getStorageSafe('has_shown_privacy_dialog', false);

        if(typeof storedPrivacyAgreedStatus == 'boolean'){
            this.setPrivacyContractAgreedStatus(storedPrivacyAgreedStatus);
        }

        if(typeof storedShownPrivacyDialogStatus == 'boolean'){
            this.setPrivacyDialogShownStatus(storedShownPrivacyDialogStatus);
        }

        this.checkAndShowPrivacyDialog();
        writeLog('privacy', 'INFO', '获取用户隐私同意相关状态完成');
    },

    checkAndShowPrivacyDialog() {
        const isPrivacyContractAgreed = this.getPrivacyContractAgreedStatus();
        const hasShownPrivacyDialog = this.getPrivacyDialogShownStatus();

        // 只要未显示过，就需要显示隐私保护指引弹窗
        if (!hasShownPrivacyDialog) {
            writeLog('privacy', 'INFO', '用户首次访问，显示隐私协议弹窗');
            this.showPrivacyDialog();
            this.setPrivacyDialogShownStatus(true);
            this.validateAndSetStorage('privacy_dialog_shown', true, 'boolean');
        }

        // 已显示过隐私保护指引弹窗
        else {
            if (!isPrivacyContractAgreed) {
                writeLog('privacy', 'INFO', '用户曾拒绝隐私协议，当前状态为拒绝');
                this.setPrivacyContractAgreedStatus(false);
                this.setPrivacyDialogShownStatus(true);
            } else {
                writeLog('privacy', 'INFO', '用户曾同意隐私协议，当前状态为同意');
                this.setPrivacyContractAgreedStatus(true);
                this.setPrivacyDialogShownStatus(true);
            }
        }
    },

    showPrivacyDialog() {
        // TODO: 显示官方隐私保护指引弹窗并作降级兜底处理（官方弹窗->自定义弹窗->无弹窗(默认为不同意)，完善隐私保护指引弹窗相关逻辑
        const localSDKVer = this.getLocalSDKVersion();
        if (versionUtils.isSDKVersionSuitable(localSDKVer, '2.32.3')) {
            writeLog('privacy', 'INFO', `当前基础库版本 ${localSDKVer} 支持官方隐私授权API`);
            this.tryOfficialPrivacyDialog();
        } else {
            writeLog('privacy', 'WARNING', `当前基础库版本 ${localSDKVer} 不支持官方隐私授权API，使用自定义弹窗`);
            this.showCustomPrivacyDialog();
        }

    },

    tryOfficialPrivacyDialog() {
        writeLog('privacy', 'INFO', '尝试显示官方隐私保护指引弹窗');
        try {
            wx.getPrivacySetting({
                success: (res) => {
                    console.log(res);
                    writeLog('privacy', 'INFO', `获取隐私设置成功`);
                    if(res.needAuthorization){
                        this.requestPrivacyAuthorize();
                    } else {
                        writeLog('privacy', 'INFO', '无需授权，直接设置为同意状态')
                        this.setPrivacyContractAgreedStatus(true);
                        this.validateAndSetStorage('is_privacy_agreed', true, 'boolean');
                    }
                },
                fail: (err) => {
                    // 异常处理，降级到自定义弹窗
                    writeLog('privacy', 'ERROR', `获取隐私设置失败: ${err.message}`);
                    this.showCustomPrivacyDialog();
                },
            });
        } catch (error) {
            writeLog('privacy', 'ERROR', `调用 getPrivacySetting 异常: ${error.message}`);
            // 异常处理，降级到自定义弹窗
            this.showCustomPrivacyDialog();
        }
    },

    requestPrivacyAuthorize() {

    },

    showCustomPrivacyDialog() {

    },

    getStorageSafe(key, defaultValue) {
        try {
            const value = wx.getStorageSync(key);
            if (value !== undefined) {
                writeLog('storage', 'DEBUG', `读取本地缓存 ${key}成功`);
                return value;
            }
            writeLog('storage', 'WARNING', `本地缓存 ${key} 不存在，将使用默认值${defaultValue}`);
            return defaultValue;
        } catch (e) {
            writeLog('storage', 'ERROR', `读取 ${key} 时发生错误: ${e.message},，将使用默认值${defaultValue}`);
            console.error(`获取 ${key} 时发生错误:`, e);
            return defaultValue;
        }
    },


    validateAndSetStorage(key, value, expectedType) {
        try {
            // 类型验证
            if (typeof value !== expectedType) {
                writeLog('storage', 'WARNING', `存储验证失败: ${key} 期望类型 ${expectedType}, 实际类型 ${typeof value}`);
                console.warn(`存储验证失败: ${key} 期望类型 ${expectedType}, 实际类型 ${typeof value}`);
                return false;
            }

            // 存储数据
            wx.setStorageSync(key, value);
            writeLog('storage', 'INFO', `成功存储 ${key}: ${value}`);
            return true;
        } catch (e) {
            writeLog('storage', 'ERROR', `存储 ${key} 时发生错误: ${e.message}`);
            console.error(`存储 ${key} 时发生错误:`, e);
            return false;
        }
    },

});
