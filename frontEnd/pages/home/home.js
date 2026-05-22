// pages/home/home.js
Page({
  data: {
      urlPath:"/pages/searchResult/searchResult",
      swiperList:[
        {
          id:0,
          url:"https://img-storage-1336210390.cos.ap-guangzhou.myqcloud.com/slider-1.jpg"
        },
        {
          id:1,
          url:"https://img-storage-1336210390.cos.ap-guangzhou.myqcloud.com/team_travel.webp"
        },
        {
          id:2,
          url:"https://img-storage-1336210390.cos.ap-guangzhou.myqcloud.com/scenery.webp"
        },
      ],
      commonFunc:[
        {
          id:0,
          name:'生成旅游路线',
          className:'route-gen',
          imgUrl:'https://img-storage-1336210390.cos.ap-guangzhou.myqcloud.com/%E6%97%85%E6%B8%B8_%E8%B7%AF%E7%BA%BF.png',
          navUrl:'/pages/routeGen/routeGen',
        },
        {
          id:1,
          name:'规划旅游方案',
          className:'trip-plan',
          imgUrl:'https://img-storage-1336210390.cos.ap-guangzhou.myqcloud.com/%E6%97%85%E8%A1%8C.png',
          navUrl:'/pages/planGen/planGen',
        },
        {
          id:2,
          name:'组队',
          className:'teamup',
          imgUrl:'../../images/navbar/teamup_active.png',
          navUrl:'/pages/teamup/teamupForm/teamupForm',
          openType:'switchTab'
        }
      ],
      article:[
        {
          id:1,
          title:'欢迎访问本站!',
          content:'寻找旅伴,尽在旅伴奇遇工坊',
          picSrc:'https://img-storage-1336210390.cos.ap-guangzhou.myqcloud.com/%E6%B8%B8%E8%AE%B0.png',
          pubDate:'2025-12-10'
        },
        {
          id:2,
          title:'使用指南',
          content:`在本站，你可通过“生成旅游路线”功能和“生成旅游方案”功能，或者运用AI助手，帮助快速找到适合自己的旅游路线和旅行方案，获得更安心、省心的旅行体验！`,
          picSrc:'https://img-storage-1336210390.cos.ap-guangzhou.myqcloud.com/%E6%97%85%E8%A1%8C.png',
          pubDate:'2026-2-6'
        },
      ],
  },

  onLoad(options) {},
  onReady() {},
  onShow() {},
  onHide() {},
  onUnload() {},
  onPullDownRefresh() {},
  onReachBottom() {},
  onShareAppMessage() {}
})