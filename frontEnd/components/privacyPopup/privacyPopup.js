import SDKVersionCompareUtils from '../../utils/SDKVersionCompareUtils.js'

Component({
  properties: {
    miniProgramName: {
      type: String,
      value: '旅伴奇遇工坊'
    }
  },
  data: {
    showPrivacy: false,
    isSuitableSDKVersion: false,
    privacyContractName: '旅伴奇遇工坊小程序隐私保护指引',
    resolvePrivacy: null
  },
  methods: {

  },
  lifetimes:{
    attached() {
      const SDKVersion = wx.getAppBaseInfo().SDKVersion
      const isSuitableSDKVersion = SDKVersionCompareUtils.isSDKVersionSuitable(SDKVersion,'2.23.3')
      this.setData({isSuitableSDKVersion})

      
    }
  }
})