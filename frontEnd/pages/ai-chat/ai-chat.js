import { writeLog } from '../../utils/loggerUtils';

Page({
  data: {
    statusBarHeight: 0,
    navBarHeight: 88,
    inputValue: '',
    messages: [],
    scrollToView: '',
    scrollAnimation: true
  },

  onLoad: function (options) {
    const systemInfo = wx.getSystemInfoSync();
    const statusBarHeight = systemInfo.statusBarHeight;
    const navBarHeight = statusBarHeight + 88;
    
    this.setData({
      statusBarHeight: statusBarHeight,
      navBarHeight: navBarHeight
    });

    writeLog('ai-chat', 'INFO', 'AI聊天页面加载成功');
  },

  onReady: function () {
    writeLog('ai-chat', 'INFO', 'AI聊天页面就绪');
  },

  onShow: function () {
    writeLog('ai-chat', 'INFO', 'AI聊天页面显示');
  },

  onInput: function (e) {
    const value = e.detail.value;
    this.setData({
      inputValue: value
    });
    writeLog('ai-chat', 'INFO', '用户输入框内容更新');
  },

  onSend: function () {
    if (!this.data.inputValue.trim()) {
      writeLog('ai-chat', 'WARNING', '尝试发送空消息');
      return;
    }

    const userInput = this.data.inputValue.trim();
    
    // 添加用户消息到列表
    const newMessages = [...this.data.messages];
    newMessages.push({
      sender: '您',
      content: userInput
    });

    this.setData({
      messages: newMessages,
      inputValue: '',
      scrollToView: `msg-${newMessages.length - 1}`
    });

    // 模拟AI回复
    setTimeout(() => {
      const aiReply = this.generateAIReply(userInput);
      
      const updatedMessages = [...this.data.messages];
      updatedMessages.push({
        sender: 'AI助手',
        content: aiReply
      });

      this.setData({
        messages: updatedMessages,
        scrollToView: `msg-${updatedMessages.length - 1}`
      });

      writeLog('ai-chat', 'INFO', 'AI回复已添加');
    }, 1000);

    // 记录发送消息事件（脱敏处理）
    writeLog('ai-chat', 'INFO', '用户发送消息（已脱敏）');
  },

  generateAIReply: function(userInput) {
    const replies = [
      '好的，关于您的问题我会尽力为您提供帮助。',
      '这是一个很好的问题，让我来帮您解答。',
      '根据您的需求，我建议您可以考虑以下几个方面...',
      '我已经收到您的问题，正在为您分析...',
      '针对您提到的内容，我可以提供专业的旅游建议。'
    ];
    
    // 根据用户输入关键词生成更相关的回复
    if (userInput.includes('旅游') || userInput.includes('旅行') || userInput.includes('路线')) {
      return '关于旅游规划，我建议您首先确定目的地、出行时间和预算。然后可以根据个人兴趣选择景点，并合理安排每日行程。记得提前预订住宿和交通工具哦！';
    } else if (userInput.includes('推荐') || userInput.includes('哪里')) {
      return '根据不同类型，我可以为您推荐热门旅游目的地：自然风光类如九寨沟、张家界；历史文化类如北京故宫、西安兵马俑；海滨度假类如三亚、青岛等。您想了解哪一类呢？';
    } else if (userInput.includes('美食') || userInput.includes('吃')) {
      return '旅游时品尝当地美食是必不可少的体验！每个地方都有独特的风味小吃和特色菜肴，比如四川的麻辣火锅、广东的早茶、北京的烤鸭等。';
    }
    
    return replies[Math.floor(Math.random() * replies.length)];
  },

  onHistoryTap: function () {
    writeLog('ai-chat', 'INFO', '点击历史图标');
    wx.showToast({
      title: '历史记录功能待实现',
      icon: 'none'
    });
  },

  onMuteTap: function () {
    writeLog('ai-chat', 'INFO', '点击静音图标');
    wx.showToast({
      title: '静音功能待实现',
      icon: 'none'
    });
  },

  onPlusTap: function () {
    writeLog('ai-chat', 'INFO', '点击加号图标');
    wx.navigateTo({
      url: '/pages/agent-select/agent-select',
      fail: (err) => {
        writeLog('ai-chat', 'WARNING', '跳转智能体选择页失败');
        wx.showModal({
          title: '提示',
          content: '智能体选择功能暂未开放',
          showCancel: false
        });
      }
    });
  },

  onMicrophoneTap: function () {
    writeLog('ai-chat', 'INFO', '点击麦克风图标');
    wx.showToast({
      title: '语音输入功能待实现',
      icon: 'none'
    });
  },

  onCameraTap: function () {
    writeLog('ai-chat', 'INFO', '点击相机图标');
    wx.showToast({
      title: '拍照功能待实现',
      icon: 'none'
    });
  },

  onQuickActionTap: function (e) {
    const action = e.currentTarget.dataset.action;
    writeLog('ai-chat', 'INFO', `执行快捷操作: ${action}`);

    let prompt = '';
    switch(action) {
      case 'travel-plan':
        prompt = '请帮我制定一个旅行计划';
        break;
      case 'route-recommend':
        prompt = '推荐一些旅游路线';
        break;
      case 'destination-info':
        prompt = '我想了解一些旅游目的地信息';
        break;
      default:
        prompt = '你好';
    }

    this.setData({
      inputValue: prompt
    });

    setTimeout(() => {
      this.onSend();
    }, 100);
  },
  
  onPageScroll: function(e) {
    if (this.scrollTimer) {
      clearTimeout(this.scrollTimer);
    }
    this.scrollTimer = setTimeout(() => {
      writeLog('ai-chat', 'INFO', '页面滚动');
    }, 300);
  }
});