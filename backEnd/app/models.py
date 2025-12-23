import random
import string
from sqlalchemy import ( 
    Column, PrimaryKeyConstraint, String, Text, Enum, DateTime, Index,
    ForeignKey, CheckConstraint, UniqueConstraint, JSON, text,event
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship,declarative_base
from sqlalchemy.dialects.mysql import INTEGER,BIGINT

Base = declarative_base()

# 后台管理员表
class Admin(Base):
    __tablename__ = 'admin'
    
    id = Column(INTEGER(unsigned=True),primary_key=True,autoincrement=True)
    username = Column(String(15),unique=True,nullable=False)
    pwd = Column(String(255),nullable=False)
    gender = Column(Enum('男','女'),nullable=True,default=None)

    notice = relationship("Notice",back_populates='admin')
    
    def __repr__(self):
        return f"<Admin(id={self.id}, username={self.username}, pwd={self.pwd},gender={self.gender})>"
    
# 行程安排表
class Arrange(Base):
    __tablename__ = 'arrange'
    
    id = Column(INTEGER(unsigned=True),primary_key=True,autoincrement=True)
    plan_id = Column(INTEGER(unsigned=True),ForeignKey('plan.id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False,index=True)
    day = Column(INTEGER(unsigned=True),nullable=False)
    title = Column(String(50),nullable=False)
    detail = Column(Text,nullable=False)
    
    plan = relationship("Plan",back_populates="arrange")
    
    __table_args__ = (
        UniqueConstraint('plan_id','day',name='uqk_planid_day'),
        CheckConstraint(day > 0,name='arrange_chk_1'),
    )
    
    def __repr__(self):
        return f"<Arrange(id={self.id}, plan_id={self.plan_id}, day={self.day}, title={self.title},detail={self.detail})>"

# 用户登录信息表
class Login(Base):
    __tablename__ = 'login'
    
    id = Column(INTEGER(unsigned=True),primary_key=True,autoincrement=True)
    user_id =  Column(INTEGER(unsigned=True),ForeignKey('user.id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False,unique=True)
    openid = Column(String(150),nullable=False,unique=True)
    session_key = Column(String(150),nullable=False,unique=True)
    token = Column(String(255),nullable=False,unique=True)
    last_login_time = Column(DateTime(timezone=True),nullable=False,server_default=func.now())
    login_source = Column(String(50),nullable=True, server_default='wechat')
    
    user = relationship("User",back_populates="login")
    def __repr__(self):
        return f"<Login(id={self.id}, user_id={self.user_id}, openid={self.openid}, session_key={self.session_key},token={self.token},last_login_time={self.last_login_time},login_source={self.login_source})>"

NoticeType = Enum('系统公告','活动公告',name='notice_type')
NoticeStatus = Enum('已发布','已归档',name='notice_status')

# 公告表
class Notice(Base):
    __tablename__ = 'notice'
    
    id = Column(INTEGER(unsigned=True),autoincrement=True,primary_key=True)
    title = Column(String(50),nullable=False)
    content = Column(Text,nullable=False)
    cover_img_url = Column(Text,nullable=True)
    type = Column(NoticeType,nullable=False,index=True)
    create_time = Column(DateTime(timezone=True),nullable=False,server_default=func.now())
    update_time = Column(DateTime(timezone=True),nullable=False,server_default=func.now(),onupdate=func.now())
    expire_time = Column(DateTime(timezone=True),nullable=True,server_default=text("'2099-12-31 23:59:59'"))
    author_id = Column(INTEGER(unsigned=True),ForeignKey('admin.id',ondelete='CASCADE'),nullable=False,index=True,unique=True)
    status = Column(NoticeStatus,nullable=False,server_default='已发布')
    
    admin = relationship("Admin",back_populates='notice')
    notice_attachments = relationship('NoticeAttachments', back_populates='notice')
    
    def __repr__(self):
        return f"<Notice(id={self.id}, title={self.title}, content={self.content},type={self.type},create_time={self.create_time},update_time={self.update_time},expire_time={self.expire_time},author_id={self.author_id},status={self.status})>"

# 公告附件表
class NoticeAttachments(Base):
    __tablename__= 'notice_attachments'
    
    id = Column(INTEGER(unsigned=True),primary_key=True,autoincrement=True)
    notice_id = Column(INTEGER(unsigned=True),ForeignKey('notice.id',ondelete='CASCADE'),nullable=False)
    file_name = Column(Text,nullable=False)
    file_url = Column(Text,nullable=False)
    description =  Column(Text)
    upload_time = Column(DateTime(timezone=True),nullable=True,server_default=func.now())
                
    notice = relationship('Notice',back_populates='notice_attachments')
    
    def __repr__(self):
        return f"NoticeAttachments(id={self.id},notice_id={self.notice_id},file_name={self.file_name},file_url={self.file_url},description={self.description},upload_time={self.upload_time})"


Duration = Enum(
    '1-3天',
    '4-7天',
    '超过7天',  
    name = 'time'
)

Budget = Enum(
    '0-1000元',
    '1000-3000元',
    '3000-5000元',
    '5000-10000元',
    '10000元以上',
    name='budget'
)

Preference = Enum(
    '登山徒步',
    '越野冒险',
    '探索历史遗迹',
    '参观名胜古迹',
    '体验当地习俗文化',
    '品尝美食',
    name = 'preference'
)

# 个性化旅游方案表
class Plan(Base):
    __tablename__='plan'
    
    id=Column(INTEGER(unsigned=True),autoincrement=True,primary_key=True)
    user_id = Column(INTEGER(unsigned=True),ForeignKey('user.id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False,index=True)
    personality = Column(String(255),nullable=False)
    hobbies = Column(String(50),nullable=False)
    duration = Column(Duration,nullable=False) # 计划旅游天数
    budget = Column(Budget,nullable=False) # 预算范围
    preference = Column(Preference,nullable=False)
    total_spending = Column(INTEGER(unsigned=True),nullable=False,index=True) # 方案预计花费
    arrange_data = Column('arrange',JSON,nullable=False)
    create_time = Column(DateTime(timezone=True),nullable=False,server_default=func.now())
    status = Column(Enum('0','1',name='planAvailableStatus'),nullable=False,server_default='0')
    
    user = relationship('User',back_populates='plan')
    arrange = relationship('Arrange',back_populates='plan')
    
    __table_args__ = (
       Index('idx_personality_hobbies_time_budget_preference', personality, hobbies, duration, budget, preference),
    )
    
    def __repr__(self):
        return  f"<Plan(id={self.id}, user_id={self.user_id}, personality={self.personality}, hobbies={self.hobbies}, time={self.duration}, budget={self.budget}, preference={self.preference},  total_spending={self.total_spending}, arrange={self.arrange_data},create_time={self.create_time}, status={self.status})>"

CommentStatus = Enum('已发布','已归档',name='comment_status')

# 帖子评论表（评论无法再次编辑,支持楼中楼评论,一经发布只能查看或删除）
class PostComment(Base):
    __tablename__ = 'post_comment'
    
    id=Column(BIGINT(unsigned=True),autoincrement=True,primary_key=True)
    user_id = Column(INTEGER(unsigned=True),ForeignKey('user.id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False,index=True)
    post_id = Column(INTEGER(unsigned=True),ForeignKey('posts.id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False,index=True)
    content = Column(Text,nullable=False)
    parent_id = Column(BIGINT(unsigned=True),ForeignKey('post_comment.id',ondelete='CASCADE',onupdate='CASCADE'),nullable=True,index=True)
    created_at = Column(DateTime(timezone=True),nullable=False,server_default=func.now())
    likes = Column(INTEGER(unsigned=True),nullable=True,default=0)
    status = Column(CommentStatus,nullable=True,server_default='已发布')
    
    user = relationship('User',back_populates='post_comments')
    post = relationship('Posts',back_populates='post_comments')
    parent = relationship('PostComment',remote_side=[id],back_populates='replies')
    replies = relationship('PostComment',back_populates='parent')
    
    def __repr__(self):
        return f"<PostComment(id={self.id}, user_id={self.user_id}, post_id={self.post_id}, content={self.content}, parent_id={self.parent_id}, created_at={self.created_at}, likes={self.likes}, status={self.status})>"
    

Category = Enum('经验分享','攻略分享','其他',name='post_category')  
PostStatus = Enum('已发布','已编辑','已归档',name='post_status')

# 帖子表（帖子发布后可多次编辑帖子，用户可谓帖子点赞或评论该帖子）
class Posts(Base):
    __tablename__ = 'posts'
    
    id=Column(INTEGER(unsigned=True),autoincrement=True,primary_key=True)
    user_id = Column(INTEGER(unsigned=True),ForeignKey('user.id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False,index=True)
    title = Column(String(50),nullable=False)
    content = Column(Text,nullable=False)
    category = Column(Category,nullable=False)
    img_url = Column(Text,nullable=True)
    created_at = Column(DateTime(timezone=True),nullable=True,server_default=func.now())
    updated_at = Column(DateTime(timezone=True),nullable=True,server_default=func.now(),onupdate=func.now())
    status = Column(PostStatus,nullable=False,server_default='已发布')
    likes = Column(INTEGER(unsigned=True),nullable=True,default=0)
    comments_count = Column(INTEGER(unsigned=True),nullable=True,default=0)
    
    user = relationship('User',back_populates='posts')
    post_comments = relationship('PostComment',back_populates='post')
    
    def __repr__(self):
        return f"<Post(id={self.id}, user_id={self.user_id}, title={self.title}, content={self.content}, category={self.category}, img_url={self.img_url}, created_at={self.created_at}, updated_at={self.updated_at}, status={self.status}, likes={self.likes}, comments_count={self.comments_count})>"

# 生成旅游路线表
class Route(Base):
    __tablename__ = 'route'
    
    id=Column(INTEGER(unsigned=True),autoincrement=True,primary_key=True)
    user_id = Column(INTEGER(unsigned=True),ForeignKey('user.id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False,index=True)
    destination = Column(String(50),nullable=False)
    travel_days = Column(INTEGER(unsigned=True),nullable=False)
    budget = Column(INTEGER(unsigned=True),nullable=True,default=0)
    preference = Column(String(100),nullable=False)
    route_description = Column(String(200),nullable=True)
    route_spots = Column(JSON,nullable=False)
    create_time = Column(DateTime(timezone=True),nullable=True,server_default=func.now())
    status = Column(Enum('0','1',name='routeAvailableStatus'),nullable=False,server_default='0',comment='可用状态，0：可用，1：被占用/不可用')    
    
    __table_args__ = (
        Index('idx_destination_travel_days_budget_preference', destination, travel_days, budget, preference),
        CheckConstraint('travel_days > 0',name='route_chk_1'),
    )
    
    user = relationship('User',back_populates='route')
    route_spots_mapping = relationship('RouteSpotsMapping',back_populates='route')
    
    def __repr__(self):
        return f"<Route(id={self.id}, user_id={self.user_id}, destination={self.destination}, travel_days={self.travel_days}, budget={self.budget}, preference={self.preference}, route_description={self.route_description}, route_spots={self.route_spots}, create_time={self.create_time}, status={self.status})>"

# 旅游路线景点关联表
class RouteSpotsMapping(Base):
    __tablename__ = 'route_spots_mapping'
    
    route_id = Column(INTEGER(unsigned=True),ForeignKey('route.id',ondelete='CASCADE',onupdate='CASCADE'))
    spot_id = Column(INTEGER(unsigned=True),ForeignKey("spots.id",ondelete='CASCADE',onupdate='CASCADE'))
    
    __table_args__ = (
        Index('spot_id',spot_id),
        PrimaryKeyConstraint(route_id, spot_id)
    )
    
    route = relationship("Route",back_populates="route_spots_mapping")
    spots = relationship("Spots",back_populates="route_spots_mapping")
    
    def __repr__(self):
        return f"<RouteSpotsMapping(route_id={self.route_id}, spot_id={self.spot_id})>"
   
# 景点表
class Spots(Base):
    __tablename__ = 'spots'
    
    id=Column(INTEGER(unsigned=True),autoincrement=True,primary_key=True)
    name = Column(String(100),nullable=False)
    location = Column(String(255),nullable=False)
    description = Column(Text,nullable=False)
    
    __table_args__ = (
        Index('location',location),
        Index('description',description,mysql_prefix='FULLTEXT')
    )
    
    route_spots_mapping = relationship("RouteSpotsMapping",back_populates="spots")
    
    def __repr__(self):
        return f"<Spot(id={self.id}, name={self.name}, location={self.location}, description={self.description})>"
    
TeamupStatus = Enum('正在组队中', '已组队成功', name='teamup_status')

# 组队表
class Teamup(Base):
    __tablename__ = 'teamup'

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    initiator_id = Column(INTEGER(unsigned=True), ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    nickname = Column(String(15), nullable=False, default='')
    gender = Column(Enum('男','女'), nullable=False)
    travel_days = Column(INTEGER(unsigned=True), nullable=False)
    budget = Column(INTEGER(unsigned=True), nullable=False, default=0)
    preference = Column(Text, nullable=False)
    pic_url = Column(Text, nullable=True)
    create_time = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    participant_id = Column(INTEGER(unsigned=True), ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    teamup_time = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    status = Column(TeamupStatus, nullable=False, server_default='正在组队中')

    __table_args__ = (
        Index('initiator_id', initiator_id),
        Index('participant_id', participant_id),
        Index('preference', preference, mysql_prefix='FULLTEXT'),
    )

    initiator = relationship("User", foreign_keys=[initiator_id], back_populates="teamups_as_initiator")
    participant = relationship("User", foreign_keys=[participant_id], back_populates="teamups_as_participant")

    def __repr__(self):
        return f"<Teamup(id={self.id}, initiator_id={self.initiator_id}, nickname={self.nickname}, gender={self.gender}, travel_days={self.travel_days}, budget={self.budget}, preference={self.preference}, pic_url={self.pic_url}, create_time={self.create_time}, participant_id={self.participant_id}, teamup_time={self.teamup_time}, status={self.status})>"

# 用户个人信息表
class User(Base):
    __tablename__ = 'user'

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    nickname = Column(String(15), nullable=False,default= lambda: User.__generate_default_nickname())
    avatar = Column(Text, nullable=False,default='https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0')
    gender = Column(Enum('男','女'), nullable=True,default=None)
    hobby = Column(String(50), nullable=True)

    __table_args__ = (
        Index('idx_gender', gender),
        Index('idx_hobby', hobby, mysql_prefix='FULLTEXT'),
    )
    plan = relationship('Plan', back_populates='user')
    login = relationship('Login', back_populates='user')
    posts = relationship('Posts', back_populates='user')
    route = relationship('Route', back_populates='user')
    teamups_as_initiator = relationship('Teamup', foreign_keys='Teamup.initiator_id', back_populates='initiator')
    teamups_as_participant = relationship('Teamup', foreign_keys='Teamup.participant_id', back_populates='participant')
    post_comments = relationship('PostComment',back_populates='user')

    def __repr__(self):
        return f"<User(id={self.id}, nickname={self.nickname}, avatar={self.avatar}, gender={self.gender}, hobby={self.hobby})>"
    
    @staticmethod
    def __generate_default_nickname():
        """
        生成小程序用户的默认用户名
        格式：旅友_ + 8位随机字符（a-z、A-Z、0-9）
        """
        PREFIX = "旅友" 
        SUFFIX_LENGTH = 8 
        CHARSET = string.ascii_letters + string.digits 
        suffix = ''.join(random.choice(CHARSET) for _ in range(SUFFIX_LENGTH))
        return f"{PREFIX}_{suffix}"
    
        
        

        

    
    
    
    