# from flask_sqlalchemy import SQLAlchemy
# import pymysql
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask import current_app
# from datetime import datetime
#
# db = SQLAlchemy()
#
#
# class BaseModel(object):
#     # 基类
#     create_time = db.Column(db.DateTime, default=datetime.now())
#     update_time = db.Column(db.DateTime, default=datetime.now())
#     isDelete = db.Column(db.Boolean, default=False)
#
#
# class NewsInfo(db.Model, BaseModel):
#     # 新闻表
#     __tablename__ = 'news_info'
#     id = db.Column(db.Integer, primary_key=True)
#     # 分类
#     category_id = db.Column(db.Integer, db.ForeignKey('news_category.id'))
#     pic = db.Column(db.String(50))
#     title = db.Column(db.String(30))
#     summary = db.Column(db.String(200))
#     context = db.Column(db.Text)
#     # 发布用户
#     user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
#     source = db.Column(db.String(20), default="")
#     click_count = db.Column(db.Integer, default=0)
#     comment_count = db.Column(db.Integer, default=0)
#     status = db.Column(db.SmallInteger, default=1)
#     reason = db.Column(db.String(100), default='')
#     # 评论   lazy 设置查询实例对象时默认不查询关系数据,使用对象.comments时才查询关系数据
#     comments = db.relationship('NewsComment', backref='news', lazy='dynamic', order_by='NewsComment.id.desc()')
#
#
# class NewsCategory(db.Model, BaseModel):
#     # 新闻分类表
#     __tablename__ = 'news_category'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(10))
#     order = db.Column(db.SmallInteger)
#     news = db.relationship('NewsInfo', backref='category', lazy='dynamic')
#
#
# class NewsComment(db.Model, BaseModel):
#     # 评论表
#     __tablename__ = 'news_comment'
#     id = db.Column(db.Integer, primary_key=True)
#     news_id = db.Column(db.Integer, db.ForeignKey('news_info.id'))
#     user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
#     like_count = db.Column(db.Integer, default=0)
#     # 被评论的评论id---自关联
#     comment_id = db.Column(db.Integer, db.ForeignKey('news_comment.id'))
#     msg = db.Column(db.String(200))
#     # 对象.comments===>找到(comment_id == 对象.id)所有对象
#     comments = db.relationship('NewsComment', lazy='dynamic')
#
#
# # 关注表
# tb_user_follow = db.Table(
#     'tb_user_follow',
#     db.Column('origin_user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True),
#     db.Column('follow_user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True)
# )
#
# # 收藏表
# tb_news_collect = db.Table('tb_news_collect',
#                            db.Column('user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True),
#                            db.Column('news_id', db.Integer, db.ForeignKey('news_info.id'), primary_key=True)
#                            )
#
#
# class UserInfo(db.Model, BaseModel):
#     # 用户表
#     __tablename__ = 'user_info'
#     id = db.Column(db.Integer, primary_key=True)
#     avatar = db.Column(db.String(50), default='user_pic.png')
#     nick_name = db.Column(db.String(20))
#     signature = db.Column(db.String(200))
#     pulic_count = db.Column(db.Integer, default=0)
#     follow_count = db.Column(db.Integer, default=0)
#     mobile = db.Column(db.String(11))
#     password_hash = db.Column(db.String(200))
#     gender = db.Column(db.Boolean, default=False)
#     isadmin = db.Column(db.Boolean, default=False)
#     # 发布的新闻
#     news = db.relationship("NewsInfo", backref='news', lazy='dynamic')
#     # 收藏新闻
#     news_collect = db.relationship(
#         'NewsInfo',
#         secondary=tb_news_collect,
#         lazy='dynamic'
#     )
#     # 用户的评论
#     comments = db.relationship('NewsComment', backref='news', lazy='dynamic')
#     # 关注的人
#     follow_user = db.relationship(
#         'UserInfo', lazy='dynamic', secondary='tb_follow_user',
#         # 1. 正向调用需要遵循的规则:关系表中 原id==此对象.id 的所有行===>即可得到所有关注的人(关系表.关注id)
#         primaryjoin=id == tb_user_follow.c.origin_user_id,
#         # 2. 逆向调用需要遵循的规则:关系表中.关注的id == 此对象.id 的所有行===>即可得到所有关注此对象的人(关系表.原id)
#         secondaryjoin=id == tb_user_follow.c.follow_user_id,
#         backref=db.backref('follow_by_user',
#                            lazy='dynamic')
#     )
#
#     @property
#     def password(self):
#         pass
#
#     @password.setter
#     def password(self, pwd):
#         self.password_hash = generate_password_hash(pwd)
#
#     def check_pwd(self, pwd):
#         return check_password_hash(self.password_hash, pwd)
import pymysql
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from datetime import datetime

pymysql.install_as_MySQLdb()

db = SQLAlchemy()


class BaseModel(object):
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now)
    isDelete = db.Column(db.Boolean, default=False)


tb_news_collect = db.Table(
    'tb_news_collect',
    db.Column('user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True),
    db.Column('news_id', db.Integer, db.ForeignKey('news_info.id'), primary_key=True)
)
tb_user_follow = db.Table(
    'tb_user_follow',
    db.Column('origin_user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True),
    db.Column('follow_user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True)
)


class NewsCategory(db.Model, BaseModel):
    __tablename__ = 'news_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    order = db.Column(db.SmallInteger)
    news = db.relationship('NewsInfo', backref='category', lazy='dynamic')


class NewsInfo(db.Model, BaseModel):
    __tablename__ = 'news_info'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('news_category.id'))
    pic = db.Column(db.String(50))
    title = db.Column(db.String(30))
    summary = db.Column(db.String(200))
    context = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    source = db.Column(db.String(20), default='')
    click_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=1)
    reason=db.Column(db.String(100),default='')
    comments = db.relationship('NewsComment', backref='news', lazy='dynamic', order_by='NewsComment.id.desc()')

    @property
    def pic_url(self):
        return current_app.config.get('QINIU_URL') + self.pic

    def to_index_dict(self):
        return {
            'id': self.id,
            'pic_url': self.pic_url,
            'title': self.title,
            'summary': self.summary,
            'author': self.user.nick_name,
            'author_avatar': self.user.avatar_url,
            'author_id': self.user_id,
            'udpate_time': self.update_time.strftime('%Y-%m-%d')
        }


class UserInfo(db.Model,BaseModel):
    __tablename__ = 'user_info'
    id = db.Column(db.Integer, primary_key=True)
    avatar = db.Column(db.String(50), default='user_pic.png')
    nick_name = db.Column(db.String(20))
    signature = db.Column(db.String(200),default='这家伙很懒什么也没有留下')
    public_count = db.Column(db.Integer, default=0)
    follow_count = db.Column(db.Integer, default=0)
    mobile = db.Column(db.String(11))
    password_hash = db.Column(db.String(200))
    gender = db.Column(db.Boolean, default=False)
    isAdmin = db.Column(db.Boolean, default=False)

    news = db.relationship('NewsInfo', backref='user', lazy='dynamic')
    comments = db.relationship('NewsComment', backref='user', lazy='dynamic')
    news_collect = db.relationship(
        'NewsInfo',
        secondary=tb_news_collect,
        lazy='dynamic'
    )
    follow_user = db.relationship(
        'UserInfo',
        secondary=tb_user_follow,
        lazy='dynamic',
        primaryjoin=id == tb_user_follow.c.origin_user_id,
        secondaryjoin=id == tb_user_follow.c.follow_user_id,
        backref=db.backref('follow_by_user', lazy='dynamic')
    )


    @property
    def follows(self):
        return self.follow_by_user.count()

    @property
    def password(self):
        pass

    @password.setter
    def password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def check_pwd(self, pwd):
        return check_password_hash(self.password_hash, pwd)

    @property
    def avatar_url(self):
        return current_app.config.get('QINIU_URL') + self.avatar


class NewsComment(db.Model, BaseModel):
    __tablename__ = 'news_comment'
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news_info.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    like_count = db.Column(db.Integer, default=0)
    comment_id = db.Column(db.Integer, db.ForeignKey('news_comment.id'))
    msg = db.Column(db.String(200))
    comments = db.relationship('NewsComment', lazy='dynamic')