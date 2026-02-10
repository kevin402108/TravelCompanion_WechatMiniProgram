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
    wx.switchTab({
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
    requestUtils.requestWithAuth('/routes/auto_generate', {
      method: 'POST',
      data: {
        destination,
        travelDays,
        budget,
        preferences
      }
    }).then((res) => {
      wx.hideLoading();
      if (res.statusCode === 200) {
        const routeData = res?.data?.data?.route;
        if (routeData) {
          const { route_id,detail} = routeData;
          this.setData({
            route_id,
            route: detail,
            tip: '已为您生成旅游路线！'
          });
        } else {
          wx.showToast({
            title: '很抱歉，未能为您生成旅游路线！',
            icon: 'none'
          });
        }
        this.setData({
          tipShow: false,
          emptyBoxShow: true
        });
      } else {
        wx.showToast({
          title: '出错了！',
          icon: 'error'
        });
        this.setData({
          tipShow: false,
          emptyBoxShow: true
        });
      }
    }).catch((err) => {
      wx.hideLoading();
      if (err.errMsg && err.errMsg.includes('timeout')) {
        wx.showToast({
          title: '请求超时,未能生成旅游路线！',
          icon: 'none',
          duration: 5000
        });
      } else {
        wx.showToast({
          title: '网络错误，请稍后再试！',
          icon: 'none'
        });
      }
      this.setData({
        tipShow: false,
        emptyBoxShow: true
      });
    });
  },

  /**
 * 删除指定景点（带二次确认 + 前端更新 + 后端同步）
 * @param {Object} e - 事件对象
 */
  deleteSpot(e) {
    const spotId = parseInt(e.currentTarget.dataset.id, 10);
    const { route_id, route } = this.data;

    writeLog('DELETE_SPOT', 'INFO', `开始删除景点 id=${spotId}，所属路线 id=${route_id}`);

    if (!route_id || isNaN(route_id) || route_id <= 0) {
      writeLog('DELETE_SPOT', 'ERROR', `route_id无效!`);
      wx.showToast({ title: '路线信息异常，请刷新重试', icon: 'none' });
      return;
    }
    if (!spotId || isNaN(spotId) || spotId <= 0) {
      writeLog('DELETE_SPOT', 'ERROR', `spot_id无效!`);
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
          writeLog('DELETE_SPOT', 'INFO', `用户取消删除景点 ${spotId}`);
        }
      },
      fail: (err) => {
        writeLog('DELETE_SPOT', 'ERROR', `showModal 调用失败: ${err.errMsg}`);
        wx.showToast({ title: '操作异常，请重试!', icon: 'none' });
      }
    });
  },

  /**
   * 实际执行删除逻辑（分离以保持清晰）
   * @private
   */
  _performDelete(spotId, routeId, currentRoute) {
    const deleteUrl = `/routes/${routeId}/spots/${spotId}`;
    requestUtils.requestWithAuth(deleteUrl, { method: 'DELETE' }).then(res => {
        if (res.statusCode === 200) {
          writeLog('DELETE_SPOT', 'INFO', `成功删除景点 ${spotId} 与路线 ${routeId} 的关联`);

          const updatedRoute = currentRoute.filter(item => item.id !== spotId);
          this.setData({ route: updatedRoute });
          wx.showToast({ title: '删除成功！', icon: 'success', duration: 1500 });
          if (updatedRoute.length === 0) {
            this.setData({ emptyBoxShow: true });
          }
        } else {
          const errMsg = res.data?.message || `删除失败（HTTP ${res.statusCode}）`;
          writeLog('DELETE_SPOT', 'WARNING', `后端返回非成功状态: ${errMsg}`);
          wx.showToast({ title: errMsg, icon: 'none' });
          this.setData({ route: currentRoute });
        }
      })
      .catch(err => {
        const errorMsg = err.errMsg || '网络请求失败';
        writeLog('DELETE_SPOT', 'ERROR', `网络异常: ${errorMsg}`);

        if (err.errMsg && err.errMsg.includes('timeout')) {
          wx.showToast({ title: '删除超时，请检查网络', icon: 'none', duration: 3000 });
        } else {
          wx.showToast({ title: '删除失败，请稍后重试', icon: 'none' });
        }
        this.setData({ route: currentRoute });
      })
      .finally(() => {
        writeLog('DELETE_SPOT', 'INFO', `操作结束，当前路线景点数: ${this.data.route.length}`);
      });
  },

  onReady() {},
  onShow() {},
  onHide() {},
  onUnload() {},
  onPullDownRefresh() {},
  onReachBottom() {},
  onShareAppMessage() {}
})