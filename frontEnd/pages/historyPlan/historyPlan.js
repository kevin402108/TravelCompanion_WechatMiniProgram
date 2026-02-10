import requestUtils from "../../utils/requestUtils";
import { writeLog } from "../../utils/loggerUtils";

const app = getApp();

Page({
  data: {
    plans: [],
    loaded: false,
    showDetailModal: false,
    detailTitle: '',
    detailPlan: null,
    detailArrangeText: ''
  },

  onLoad() {
    wx.showLoading({ title: '加载中...' });
    this.loadPlans();
  },

  loadPlans() {
    writeLog('HISTORY_PLAN', 'INFO', '开始加载历史方案');
    requestUtils.requestWithAuth('/plans', { method: 'GET' })
      .then(res => {
        wx.hideLoading();
        if (res.statusCode === 200) {
          const plans = (res.data?.data?.plans || []).map(p => ({
            ...p,
            create_time: p.create_time
              ? new Date(p.create_time).toLocaleString('zh-CN', {
                  year: 'numeric', month: '2-digit', day: '2-digit',
                  hour: '2-digit', minute: '2-digit'
                }) : '未知时间'
          }));
          this.setData({ plans, loaded: true });
          writeLog('HISTORY_PLAN', 'INFO', `加载成功，共 ${plans.length} 条`);
        } else {
          this.setData({ plans: [], loaded: true });
          wx.showToast({ title: '加载失败', icon: 'none' });
        }
      })
      .catch(err => {
        wx.hideLoading();
        writeLog('HISTORY_PLAN', 'ERROR', `网络异常: ${err.errMsg}`);
        this.setData({ plans: [], loaded: true });
        wx.showToast({ title: '网络错误，请重试', icon: 'none' });
      });
  },

  confirmDelete(e) {
    const id = e.currentTarget.dataset.id;
    const plan = this.data.plans.find(p => p.id === id);
    if (!plan) return;

    wx.showModal({
      title: '确认删除',
      content: `确定要删除该个性化方案吗？`,
      confirmText: '确认删除',
      cancelText: '取消',
      success: res => res.confirm && this.deletePlan(id),
      fail: err => writeLog('HISTORY_PLAN', 'ERROR', `showModal 失败: ${err.errMsg}`)
    });
  },

  deletePlan(planId) {
    requestUtils.requestWithAuth(`/plans/${planId}`, { method: 'DELETE' })
      .then(res => {
        if (res.statusCode === 200) {
          wx.showToast({ title: '删除成功！', icon: 'success' });
          this.setData({
            plans: this.data.plans.filter(p => p.id !== planId)
          });
        } else {
          wx.showToast({ title: res.data?.message || '删除失败', icon: 'none' });
        }
      })
      .catch(() => {
        wx.showToast({ title: '删除失败，请重试', icon: 'none' });
      });
  },

  showPlanDetail(e) {
    const id = e.currentTarget.dataset.id;
    const plan = this.data.plans.find(p => p.id === id);
    if (!plan) return;

    this.setData({
      showDetailModal: true,
      detailTitle: plan.budget + " 元方案",
      detailPlan: plan,
      detailArrangeText: (plan.arrange || []).map(a => a.title).join('、') || '无'
    });
  },

  hideDetailModal() {
    this.setData({ showDetailModal: false, detailPlan: null });
  },

  onPullDownRefresh() {
    this.loadPlans();
    wx.stopPullDownRefresh();
  }
});
