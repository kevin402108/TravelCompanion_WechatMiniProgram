import requestUtils from "../../../utils/requestUtils";
import {writeLog} from "../../../utils/loggerUtils";
const app = getApp();

Page({
  data: {
    tip: '',
    destination: '',
    travelDays: '',
    budget: '',
    preferences: '',
    route: [],
    route_id: null,
    tipShow: true,
    emptyBoxShow: false
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

  navigateToAIPlan() {
    wx.navigateTo({
      url: '/pages/ai-chat/ai-chat',
    });
  },

  navigateToHistory() {
    wx.navigateTo({
      url: '/pages/historyRoutes/historyRoutes'
    });
  },

  getRoute: function () {
    wx.showLoading({
      title: '生成路线中...'
    });

    const { destination, travelDays, budget, preferences } = this.data;
    // requestUtils.requestWithAuth('/routes/auto_generate', {
    //   method: 'POST',
    //   data: {
    //     destination,
    //     travelDays,
    //     budget,
    //     preferences
    //   }
    // }).then((res) => {
    //   wx.hideLoading();
    //   if (res.statusCode === 200) {
    //     const routeData = res?.data?.data?.route;
    //     if (routeData) {
    //       const { route_id,detail} = routeData;
    //       this.setData({
    //         route_id,
    //         route: detail,
    //         tip: '已为您生成旅游路线！'
    //       });
    //     } else {
    //       wx.showToast({
    //         title: '很抱歉，未能为您生成旅游路线！',
    //         icon: 'none'
    //       });
    //     }
    //     this.setData({
    //       tipShow: false,
    //       emptyBoxShow: true
    //     });
    //   } else {
    //     wx.showToast({
    //       title: '出错了！',
    //       icon: 'error'
    //     });
    //     this.setData({
    //       tipShow: false,
    //       emptyBoxShow: true
    //     });
    //   }
    // }).catch((err) => {
    //   wx.hideLoading();
    //   if (err.errMsg && err.errMsg.includes('timeout')) {
    //     wx.showToast({
    //       title: '请求超时,未能生成旅游路线！',
    //       icon: 'none',
    //       duration: 5000
    //     });
    //   } else {
    //     wx.showToast({
    //       title: '网络错误，请稍后再试！',
    //       icon: 'none'
    //     });
    //   }
    //   this.setData({
    //     tipShow: false,
    //     emptyBoxShow: true
    //   });
    // });
    setTimeout(() => {
      wx.hideLoading();
      this.setData({
            route_id:1,
            route: [
                        {
                            "id" : 1 ,
                            "name" : "遇龙河" ,
                            "description" : "遇龙河是一条较为宁静的河流，水流平缓，周围环绕着喀斯特山峰。您可以选择竹筏漂流或划船，享受水清山绿的宁静与美丽，远离游客的喧嚣，体验与大自然亲密接触的感觉。" ,
                        } ,
                        {
                            "id" : 2 ,
                            "name" : "漓江" ,
                            "description" : "漓江的山水景色被誉为世界上最美的河流之一。沿江的喀斯特山脉如画卷般展开，水面清澈，群山倒影。您可以选择竹筏漂流，或者在江边徒步，沉浸在这一片美丽的自然风光中。" ,
                        } ,
                        {
                            "id" : 3 ,
                            "name" : "龙脊梯田" ,
                            "description" : "位于桂林以北，龙脊梯田是一个少人打扰的景区，可以深入自然环境中，欣赏一望无际的梯田景色。每个季节的景色都不同，春天水田倒影，秋冬则是金黄的稻谷季节。" ,
                        } ,
                        {
                            "id" : 4 ,
                            "name" : "龙胜温泉" ,
                            "description" : "龙胜温泉位于桂林周边山区，远离喧嚣的城市，温泉水质优良，被群山环绕，是放松心情、恢复体力的好地方。环境安静，适合在大自然中休养生息。" ,
                        } ,
                        {
                            "id" : 6 ,
                            "name" : "黄布倒影" ,
                            "description" : "黄布倒影是漓江沿线的著名景点，因水中山的倒影形成了如画的景致。这里人少、风景美，是一个宁静的观光地，您可以在这里享受桂林山水的自然美。" ,
                        } ,
                    ],
            tip: '已为您生成旅游路线！'
        });
    }, 3000);
  },

  /**
 * 删除指定景点（带二次确认 + 前端更新 + 后端同步）
 * @param {Object} e - 事件对象
 */
  deleteSpot(e) {
    const spotId = parseInt(e.currentTarget.dataset.id, 10);
    const { route_id, route } = this.data;

    //writeLog('DELETE_SPOT', 'INFO', `开始删除景点 id=${spotId}，所属路线 id=${route_id}`);

    if (!route_id || isNaN(route_id) || route_id <= 0) {
      //writeLog('DELETE_SPOT', 'ERROR', `route_id无效!`);
      wx.showToast({ title: '路线信息异常，请刷新重试', icon: 'none' });
      return;
    }
    if (!spotId || isNaN(spotId) || spotId <= 0) {
      //writeLog('DELETE_SPOT', 'ERROR', `spot_id无效!`);
      wx.showToast({ title: '景点ID无效', icon: 'none' });
      return;
    }

    wx.showModal({
      title: '温馨提示',
      content: `确定要移除该景点吗?`,
      confirmText: '确认移除',
      confirmColor: '#ff0202',
      cancelText: '取消',
      success: (res) => {
        if (res.confirm) {
          this._performDelete(spotId, route_id, route);
        } else {
          //writeLog('DELETE_SPOT', 'INFO', `用户取消删除景点 ${spotId}`);
        }
      },
      fail: (err) => {
        //writeLog('DELETE_SPOT', 'ERROR', `showModal 调用失败: ${err.errMsg}`);
        wx.showToast({ title: '操作异常，请重试!', icon: 'none' });
      }
    });
  },

  /**
   * 实际执行删除逻辑（分离以保持清晰）
   * @private
   */
  _performDelete(spotId, routeId, currentRoute) {
    // const deleteUrl = `/routes/${routeId}/spots/${spotId}`;
    // requestUtils.requestWithAuth(deleteUrl, { method: 'DELETE' }).then(res => {
    //     if (res.statusCode === 200) {
    //       //writeLog('DELETE_SPOT', 'INFO', `成功删除景点 ${spotId} 与路线 ${routeId} 的关联`);

    //       const updatedRoute = currentRoute.filter(item => item.id !== spotId);
    //       this.setData({ route: updatedRoute });
    //       wx.showToast({ title: '删除成功！', icon: 'success', duration: 1500 });
    //       if (updatedRoute.length === 0) {
    //         this.setData({ emptyBoxShow: true });
    //       }
    //     } else {
    //       const errMsg = res.data?.message || `删除失败（HTTP ${res.statusCode}）`;
    //       //writeLog('DELETE_SPOT', 'WARNING', `后端返回非成功状态: ${errMsg}`);
    //       wx.showToast({ title: errMsg, icon: 'none' });
    //       this.setData({ route: currentRoute });
    //     }
    //   })
    //   .catch(err => {
    //     const errorMsg = err.errMsg || '网络请求失败';
    //     //writeLog('DELETE_SPOT', 'ERROR', `网络异常: ${errorMsg}`);

    //     if (err.errMsg && err.errMsg.includes('timeout')) {
    //       wx.showToast({ title: '删除超时，请检查网络', icon: 'none', duration: 3000 });
    //     } else {
    //       wx.showToast({ title: '删除失败，请稍后重试', icon: 'none' });
    //     }
    //     this.setData({ route: currentRoute });
    //   })
    //   .finally(() => {
    //     //writeLog('DELETE_SPOT', 'INFO', `操作结束，当前路线景点数: ${this.data.route.length}`);
    //   });

    const updatedRoute = currentRoute.filter(item => item.id !== spotId);
    this.setData({ route: updatedRoute });
    wx.showToast({ title: '删除成功！', icon: 'success', duration: 1500 });
    if (updatedRoute.length === 0) {
      this.setData({ emptyBoxShow: true });
    }
  },

  onReady() {},
  onShow() {},
  onHide() {},
  onUnload() {},
  onPullDownRefresh() {},
  onReachBottom() {},
  onShareAppMessage() {}
})