from flask import Blueprint, request, make_response, session, jsonify, render_template, redirect,current_app
from utils.captcha.captcha import captcha
from utils.ytx_sdk.ytx_send import sendTemplateSMS
import random
import re
import functools
from models import db, UserInfo,NewsCategory,NewsInfo
from utils.qiniuyun_xjzx import pic1
user_blueprint = Blueprint('user', __name__, url_prefix='/user')
import datetime


# 图片验证码视图
@user_blueprint.route('/image_yzm')
def image_yzm():
    # generate_captcha()方法生成:名字,验证码,验证码图片
    name, text, content = captcha.generate_captcha()

    # 将验证码图片存在session中用来验证
    session['image_yzm'] = text
    print(session['image_yzm'])

    # make_response函数指定发送的文件类型--->jpg
    response = make_response(content)
    response.mimetype = 'image/jpg'

    return response


# 短信验证码
@user_blueprint.route('/msg_yzm', methods=['GET'])
def msg_yzm():
    dict1 = request.args

    mobile = dict1.get('mobile')

    image_yzm = dict1.get('image_yzm')

    # 检测手机号是否合法+
    if len(mobile) != 11:
        return jsonify(error_info='手机号不合法')

    if UserInfo.query.filter_by(mobile=mobile).count():
        return jsonify(error_info='该手机号已经被注册过')

    # 检测图片验证码是否正确
    if image_yzm != session['image_yzm']:
        return jsonify(error_info='验证码不合法')

    # 发送短信验证码
    # sendTemplateSMS()
    # 测试阶段使用以下方式代替
    msg_yzm = random.randint(1000, 10000)
    print(msg_yzm)
    session['msg_yzm'] = str(msg_yzm)
    return jsonify(success_info="短信已发送,请注意查收")


# 注册
@user_blueprint.route('/register', methods=['POST'])
def register():
    dict1 = request.form
    mobile = dict1.get('mobile')
    image_yzm = dict1.get('image_yzm')
    msg_yzm = dict1.get('msg_yzm')
    password = dict1.get('password')
    if not all((mobile, image_yzm, msg_yzm, password)):
        return jsonify(error_info='数据填写不完整')
    if len(mobile) != 11:
        return jsonify(error_info='手机号不合法')
    if UserInfo.query.filter_by(mobile=mobile).count():
        return jsonify(error_info='该手机号已经被注册过')
    if image_yzm != session['image_yzm']:
        return jsonify(error_info='图片验证码不正确')
    if msg_yzm != session['msg_yzm']:
        return jsonify(error_info='短信验证码不正确')
    if not re.match(r'\w{6,20}', password):
        return jsonify(error_info='密码格式不正确')
    user = UserInfo()
    user.mobile = mobile
    user.nick_name = mobile
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(success_info='注册成功,请登录')
    except:
        return jsonify(error_info='服务器出错')


# 登录
@user_blueprint.route('/login', methods=['POST'])
def login():
    dict1 = request.form
    mobile = dict1.get('mobile')
    password = dict1.get('password')
    if not all((mobile, password)):
        return jsonify(error_info='数据填写不完整')
    if len(mobile) != 11:
        return jsonify(error_info='手机号不合法')
    user = UserInfo.query.filter_by(mobile=mobile).first()
    if not user:
        return jsonify(error_info='该手机号没有注册过哦')
    if not user.check_pwd(password):
        return jsonify(error_info='密码输入错误')
    session['user_id'] = user.id
    user.update_time = datetime.datetime.now()
    db.session.commit()

    # 记录时间段内的登录用户数量
    now=datetime.datetime.now()
    name = 'active%d%d%d'%(now.year,now.month,now.day)
    for i in range(8,20):
        if not current_app.redis_client.hget(name,'%02d:15'%i):
            current_app.redis_client.hset(name, '%02d:15'%i,0)
    if now.hour<=9 or now.hour>=20:
        current_app.redis_client.hset(name,'08:15' if now.hour<=9 else '19:15',int(current_app.redis_client.hget(name,'08:15' if now.hour<=9 else '19:15').decode())+1)
    else:
        current_app.redis_client.hset(name, '%02d:15'%(now.hour-1) if now.minute <= 15 else '%02d:15'%now.hour, int(current_app.redis_client.hget(name, '%02d:15'%(now.hour-1) if now.minute <= 15 else '%02d:15'%now.hour).decode()) + 1)
    return jsonify(success_info='登录成功', nick_name=user.nick_name,avatar_url=user.avatar_url)


# 退出
@user_blueprint.route('/logout')
def logout():
    session.pop('user_id')
    return jsonify(success_info='退出成功')


# 设置登录过才展示以下页面
def check_login(func):
    @functools.wraps(func)
    def start(*args,**kwargs):
        if 'user_id' in session:
            return func(*args,**kwargs)
        else:
            return redirect('/')
    return start


# 显示用户中心视图
@user_blueprint.route('/')
@check_login
def user_index():
    user = UserInfo.query.get(session['user_id'])
    return render_template('news/user.html', title='用户中心',user=user)


# 用户基本信息
@user_blueprint.route('/base',methods=['GET','POST'])
@check_login
def base():
    user = UserInfo.query.get(session['user_id'])
    if request.method == 'GET':
        return render_template('news/user_base_info.html',user=user)
    elif request.method == 'POST':
        dict1 = request.form
        signature = dict1.get('signature')
        nick_name = dict1.get('nick_name')
        gender = bool(dict1.get('gender'))
        try:
            user.signature=signature
            user.nick_name=nick_name
            user.gender=gender
            db.session.commit()
            return jsonify(success_info='修改个人信息成功')
        except:
            return jsonify(error_info='服务器出错')


# 用户头像
@user_blueprint.route('/pic',methods=['GET','POST'])
@check_login
def pic():
    user = UserInfo.query.get(session['user_id'])
    if request.method == 'GET':
        return render_template('news/user_pic_info.html',user=user)
    elif request.method == 'POST':
        # 获得头像需要files方法
        user_pic = request.files.get('avatar')
        # 将头像传到七牛云并返回一个文件名
        avatar = pic1(user_pic)
        try:
            user.avatar = avatar
            db.session.commit()
            return jsonify(success_info='修改成功',avatar_url = user.avatar_url)
        except:
            return jsonify(error_info='服务器出错')



# 用户关注的人
@user_blueprint.route('/follow')
@check_login
def follow():
    user = UserInfo.query.get(session['user_id'])
    # 获取当前页码
    page = int(request.args.get('page',1))
    # 模板需要分页显示,需要pagination对象
    pagination = user.follow_user.paginate(page,4,False)
    user_follow_list = pagination.items
    total_page = pagination.pages
    return render_template('news/user_follow.html',user_follow_list=user_follow_list,total_page=total_page,page=page)


# 用户密码
@user_blueprint.route('/password',methods=['GET','POST'])
@check_login
def password():
    user = UserInfo.query.get(session['user_id'])
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')
    elif request.method == 'POST':
        dict1 = request.form
        old_password = dict1.get('old_password')
        new_password = dict1.get('new_password')
        new_password_config = dict1.get('new_password_config')
        if not re.match(r'\w{6,20}',old_password):
            return render_template('news/user_pass_info.html',error_info='旧密码输入格式不正确')
        if not re.match(r'\w{6,20}',new_password):
            return render_template('news/user_pass_info.html',error_info='新密码输入格式不正确')
        if new_password == old_password:
            return render_template('news/user_pass_info.html',error_info='新密码不能与旧密码一致哦')
        if new_password != new_password_config:
            return render_template('news/user_pass_info.html',error_info='两次新密码输入不一致')
        if not user.check_pwd(old_password):
            return render_template('news/user_pass_info.html',error_info='旧密码输入有误')
        try:
            user.password = new_password
            db.session.commit()
            session.pop('user_id')
            return render_template('news/user_pass_info.html',success_info='修改成功,请重新登录')
        except:
            return render_template('news/user_pass_info.html',error_info='服务器出错,请稍后重试')




# 用户收藏
@user_blueprint.route('/collection')
@check_login
def collection():
    user = UserInfo.query.get(session['user_id'])
    # 分页操作
    page = int(request.args.get('page',1))
    pagination = user.news_collect.order_by(NewsInfo.id.desc()).paginate(page,6,False)
    tatol_page = pagination.pages
    news_collect_list = pagination.items
    return render_template('news/user_collection.html',page=page,tatol_page=tatol_page,news_collect_list=news_collect_list)


# 用户发布
@user_blueprint.route('/release',methods=['GET','POST'])
@check_login
def release():
    user = UserInfo.query.get(session['user_id'])
    category_list = NewsCategory.query.all()
    try:
        # 有带新闻参数的get方式请求,认为是修改新闻的请求
        news_id = int(request.args.get('news_id'))
        news = NewsInfo.query.get(news_id)
    except:
        news = None
    if request.method == 'GET':
        # news为NewsInfo对象或者None,当为None时,模板中即不显示值
        return render_template('news/user_news_release.html', category_list=category_list,news=news)
    elif request.method == 'POST':
        dict1 = request.form
        title = dict1.get('title')
        category_id = int(dict1.get('category'))
        summary = dict1.get('summary')
        context = dict1.get('content')
        try:
            __news_pic = request.files.get('news_pic')
            news_picname = pic1(__news_pic)
        except:
            # 用户没有上传图片,则存值空字符串
            news_picname=''
        if not all((title,category_id,summary,context)):
            # html中存在要用到news的html,错误信息回传时,也需要传news对象
            return render_template('news/user_news_release.html',category_list=category_list,error_info='您的内容没有填写完整哦',news=news)
        try:
            if news:
                # 如果是修改操作,不用传用户id,
                news.update_time=datetime.now()
            else:
                news = NewsInfo()
                news.user_id = user.id
            # 如果获取到了上传的图片文件,就上传或者修改
            if news_picname:
                news.pic = news_picname
            news.title = title
            news.category_id=category_id
            news.summary=summary
            news.status = 1
            news.context = context
            db.session.add(news)
            db.session.commit()
            # 数据添加成功后默认去到新闻列表页
            return redirect('/user/list')
        except:
            return render_template('news/user_news_release.html',category_list=category_list,error_info='服务器出错',news=news)

# 用户新闻列表
@user_blueprint.route('/list')
@check_login
def list():
    user = UserInfo.query.get(session['user_id'])
    page = int(request.args.get('page',1))
    # 分页显示
    pagination = user.news.order_by(NewsInfo.id.desc()).paginate(page,6,False)
    news_list = pagination.items
    total_news = pagination.pages
    return render_template('news/user_news_list.html',page=page,news_list=news_list,total_news=total_news)

