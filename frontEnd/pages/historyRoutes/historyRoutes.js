// pages/historyRoutes/historyRoutes.js
import requestUtils from "../../utils/requestUtils";
import { writeLog } from "../../utils/loggerUtils";
const app = getApp();

Page({
  data: {
    routes: [],
    loaded: false,
    showDetailModal: false,
    detailTitle: '',
    detailRoute: null,
    detailSpotsText: ''
  },

  onLoad() {
    wx.showLoading({ title: '加载中...' });
    this.loadRoutes();
    wx.hideLoading();
  },

  loadRoutes() {
    writeLog('HISTORY_ROUTES', 'INFO', '开始加载历史路线');
    requestUtils.requestWithAuth('/routes', { method: 'GET' })
      .then(res => {
        if (res.statusCode === 200) {
          const routes = (res.data?.data?.routes || []).map(r => ({
            ...r,
            create_time: r.create_time
              ? new Date(r.create_time).toLocaleString('zh-CN', {
                  year: 'numeric', month: '2-digit', day: '2-digit',
                  hour: '2-digit', minute: '2-digit'
                }) : '未知时间'
          }));
          this.setData({ routes, loaded: true });
          writeLog('HISTORY_ROUTES', 'INFO', `加载成功，共 ${routes.length} 条`);
        } else {
          this.setData({ routes: [], loaded: true });
          wx.showToast({ title: '加载失败', icon: 'none' });
        }
      })
      .catch(err => {
        writeLog('HISTORY_ROUTES', 'ERROR', `网络异常: ${err.errMsg}`);
        this.setData({ routes: [], loaded: true });
        wx.showToast({ title: '网络错误，请重试', icon: 'none' });
      });
  },

  confirmDelete(e) {
    const id = e.currentTarget.dataset.id;
    const route = this.data.routes.find(r => r.id === id);
    if (!route) return;

    wx.showModal({
      title: '确认删除',
      content: `确定要删除这条路线吗？`,
      confirmText: '确认删除',
      confirmColor: '#ff0202',
      cancelText: '取消',
      success: res => res.confirm && this.deleteRoute(id),
      fail: err => writeLog('HISTORY_ROUTES', 'ERROR', `showModal 调用失败: ${err.errMsg}`)
    });
  },

  deleteRoute(routeId) {
    requestUtils.requestWithAuth(`/routes/${routeId}`, { method: 'DELETE' })
      .then(res => {
        if (res.statusCode === 200) {
          wx.showToast({ title: '删除成功！', icon: 'success' });
          this.setData({
            routes: this.data.routes.filter(r => r.id !== routeId)
          });
        } else {
          wx.showToast({ title: res.data?.message || '删除失败', icon: 'none' });
        }
      })
      .catch(() => {
        wx.showToast({ title: '删除失败，请重试', icon: 'none' });
      });
  },

  showRouteDetail(e) {
    const id = e.currentTarget.dataset.id;
    const route = this.data.routes.find(r => r.id === id);
    if (!route) return;

    this.setData({
      showDetailModal: true,
      detailTitle: route.destination,
      detailRoute: route,
      detailSpotsText: (route.spots || []).map(s => s.name).join('、') || '无'
    });
  },

  hideDetailModal() {
    this.setData({
      showDetailModal: false,
      detailRoute: null
    });
  },

  onPullDownRefresh() {
    this.loadRoutes();
    wx.stopPullDownRefresh();
  }
});
