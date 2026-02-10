import random
import string
from sqlalchemy import (
    Column, PrimaryKeyConstraint, String, Text, Enum, DateTime, Index,
    ForeignKey, CheckConstraint, UniqueConstraint, JSON
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship,declarative_base
from sqlalchemy.dialects.mysql import INTEGER,BIGINT

Base = declarative_base()

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
        CheckConstraint('day > 0',name='arrange_chk_1'),
        Index('plan_id', 'plan_id'),
    )

# 旅游天数
Duration = Enum('1-3天','4-7天','超过7天', name = 'time')

# 旅游预算
Budget = Enum('0-1000元','1000-3000元','3000-5000元','5000-10000元','10000元以上',name='budget')

# 旅游偏好
Preference = Enum('登山徒步','越野冒险','探索历史遗迹','参观名胜古迹','体验当地习俗文化','品尝美食',name = 'preference')

# 个性化旅游方案表
class Plan(Base):
    __tablename__='plan'
    
    id=Column(INTEGER(unsigned=True),autoincrement=True,primary_key=True)
    user_id = Column(INTEGER(unsigned=True),ForeignKey('user.id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False,index=True)
    personality = Column(String(255),nullable=False)
    hobbies = Column(String(50),nullable=False)
    duration = Column(Duration,nullable=False)
    budget = Column(Budget,nullable=False)
    preference = Column(Preference,nullable=False)
    total_spending = Column(INTEGER(unsigned=True),nullable=False,index=True)
    arrange_data = Column('arrange_data',JSON,nullable=False)
    create_time = Column(DateTime(timezone=True),nullable=False,server_default=func.now())
    status = Column(Enum('0','1',name='planAvailableStatus'),nullable=False,server_default='0')
    
    user = relationship('User',back_populates='plan')
    arrange = relationship('Arrange',back_populates='plan')
    
    __table_args__ = (
       Index('user_id', 'user_id'),
       Index('idx_personality_hobbies_time_budget_preference', 'personality', 'hobbies', 'duration', 'budget', 'preference'),
    )

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

    __table_args__ = (
        Index('user_id', 'user_id'),
        Index('post_id', 'post_id'),
        Index('parent_id', 'parent_id'),
    )

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

    __table_args__ = (
        Index('user_id', 'user_id'),
    )


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
        Index('destination', 'destination', 'travel_days', 'budget', 'preference'),
        CheckConstraint('travel_days > 0', name='route_chk_1'),
    )
    
    user = relationship('User',back_populates='route')
    route_spots_mapping = relationship('RouteSpotsMapping',back_populates='route')

# 旅游路线景点关联表
class RouteSpotsMapping(Base):
    __tablename__ = 'route_spots_mapping'

    route_id = Column(INTEGER(unsigned=True),ForeignKey('route.id',ondelete='CASCADE',onupdate='CASCADE'),primary_key=True)
    spot_id = Column(INTEGER(unsigned=True),ForeignKey("spots.id",ondelete='CASCADE',onupdate='CASCADE'),primary_key=True)

    __table_args__ = (
        Index('spot_id', 'spot_id'),
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
        Index('initiator_id', 'initiator_id'),
        Index('participant_id', 'participant_id'),
        Index('preference', preference, mysql_prefix='FULLTEXT'),
    )

    initiator = relationship("User", foreign_keys=[initiator_id], back_populates="teamups_as_initiator")
    participant = relationship("User", foreign_keys=[participant_id], back_populates="teamups_as_participant")

# 用户个人信息表
class User(Base):
    __tablename__ = 'user'
    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    openid = Column(String(150),nullable=False,unique=True)
    nickname = Column(String(15), nullable=False,default=lambda:User.generate_default_nickname())
    avatar = Column(Text, nullable=False,default='https://img-storage-1336210390.cos.ap-guangzhou.myqcloud.com/%E6%97%85%E8%A1%8C.png')
    gender = Column(Enum('男','女'), nullable=True,default=None)
    hobby = Column(String(50), nullable=True,default=None)
    create_time = Column(DateTime(timezone=True),nullable=False,server_default=func.now())
    last_login_time = Column(DateTime(timezone=True),nullable=True,server_default=func.now())
    login_source = Column(String(30),nullable=True, server_default='wechat')

    __table_args__ = (
        Index('openid', 'openid', unique=True),
        Index('idx_gender', 'gender'),
        Index('idx_hobby', 'hobby')
    )

    plan = relationship('Plan', back_populates='user')
    posts = relationship('Posts', back_populates='user')
    route = relationship('Route', back_populates='user')
    teamups_as_initiator = relationship('Teamup', foreign_keys='Teamup.initiator_id', back_populates='initiator')
    teamups_as_participant = relationship('Teamup', foreign_keys='Teamup.participant_id', back_populates='participant')
    post_comments = relationship('PostComment',back_populates='user')

    @staticmethod
    def generate_default_nickname():
        """
        生成小程序用户的默认用户名
        格式：旅友_ + 8位随机字符（a-z、A-Z、0-9）
        """
        PREFIX = "旅友"
        SUFFIX_LENGTH = 8
        CHARSET = string.ascii_letters + string.digits
        suffix = ''.join(random.choice(CHARSET) for _ in range(SUFFIX_LENGTH))
        return f"{PREFIX}_{suffix}"

    
        
        

        

    
    
    
    