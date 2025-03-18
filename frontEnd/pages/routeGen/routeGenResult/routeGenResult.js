const app = getApp()

Page({
  data: {
    tip: '',
    destination: '',
    travelDays: '',
    budget: '',
    preferences: '',
    route: '',
    tipShow: true,
    emptyBoxShow: false
  },

  getRoute: function () {
    wx.showLoading({
      title: '生成路线中...'
    })

    // POST请求 将数据发送到后端，并从后端获取生成的旅游路线( 后端接口? )
    /*  const {token,destination,travelDays,budget,preferences} = this.data
     wx.request({
       url:'#', 
       data: {token,destination,travelDays,budget,preferences},
       method:'POST',
       success:(res)=>{
         console.log(res)
         wx.hideLoading()
         if(res.statusCode == 200){
           const {route} = res.data.data
           if(route){
             this.setData({
               route:res.data.route,
               tip:'已为您生成旅游路线！'
             })
           } else {
             //未能生成旅游路线
             wx.showToast({
               title:'很抱歉，未能为您生成旅游路线！',
               icon:'none',
             })}
             this.setData({
               tipShow:false,
               emptyBoxShow:true
             })
           }
       },
       fail:(err)=>{
         wx.hideLoading()
         if (err.errMsg.includes('timeout')) {
           wx.showToast({
             title: '出错了,未能生成旅游路线！',
             icon:'none',
           })
           this.setData({
             tipShow:false,
             emptyBoxShow:true
           })
         }
       }
     }) */
    setTimeout(() => {
      wx.hideLoading()
      this.setData({
        tip: '已为您生成以下旅游路线',
        route: [
          { id: 1, name: '遇龙河', description: '遇龙河是一条较为宁静的河流，水流平缓，周围环绕着喀斯特山峰。您可以选择竹筏漂流或划船，享受水清山绿的宁静与美丽，远离游客的喧嚣，体验与大自然亲密接触的感觉。' },
          { id: 2, name: '漓江', description: '漓江的山水景色被誉为世界上最美的河流之一。沿江的喀斯特山脉如画卷般展开，水面清澈，群山倒影。您可以选择竹筏漂流，或者在江边徒步，沉浸在这一片美丽的自然风光中。' },
          { id: 3, name: '龙脊梯田', description: '位于桂林以北，龙脊梯田是一个少人打扰的景区，可以深入自然环境中，欣赏一望无际的梯田景色。每个季节的景色都不同，春天水田倒影，秋冬则是金黄的稻谷季节。' },
          { id: 4, name: '龙胜温泉', description: '龙胜温泉位于桂林周边山区，远离喧嚣的城市，温泉水质优良，被群山环绕，是放松心情、恢复体力的好地方。环境安静，适合在大自然中休养生息。' },
          { id: 5, name: '白沙古镇', description: '白沙古镇充满历史感，古老的街道和传统的建筑风格给人一种穿越时空的感觉。周围自然景观迷人，适合远足和沉浸式体验，远离繁华的市区，是感受桂林传统与自然的好去处。' },
          { id: 6, name: '黄布倒影', description: '黄布倒影是漓江沿线的著名景点，因水中山的倒影形成了如画的景致。这里人少、风景美，是一个宁静的观光地，您可以在这里享受桂林山水的自然美。' },
        ],
        tipShow: true,
        emptyBoxShow: false
      })

      /* wx.showToast({
        title: '路线生成失败！',
        icon: 'error',
        duration: 2000,
      })

      this.setData({
        tipShow:false,
        emptyBoxShow:true
      }) */
    }, 5000)
  },

  onLoad(options) {
    this.setData({
      token: app.globalData.token,
      destination: decodeURIComponent(options.destination || ''),
      travelDays: decodeURIComponent(options.travelDays || ''),
      budget: decodeURIComponent(options.budget || ''),
      preferences: decodeURIComponent(options.preferences || ''),
      tip: '正在为您生成旅游路线中...',
      route: '',
      tipShow: true,
      emptyBoxShow: false
    })
    this.getRoute()
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