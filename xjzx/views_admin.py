from flask import Blueprint,render_template,request,abort,jsonify,session,redirect,g,current_app
from flask.ext.script import Command
from models import UserInfo,db
import datetime
import random

admin_blueprint = Blueprint('admin',__name__,url_prefix='/admin')

# 创建管理员账户--->此类用于拓展命令
class CreateAdmin(Command):
    def run(self):
        mobile = input('请输入账号:')
        password = input("请输入密码")
        user = UserInfo()
        user.mobile = mobile
        user.password = password
        user.isAdmin = True
        db.session.add(user)
        db.session.commit()


# 创建用户账户--->此类用于拓展命令
class CreateUser(Command):
    def run(self):
        now = datetime.datetime.now()
        user_list=[]
        for i in range(0000,1000):
            user = UserInfo()
            user.nick_name='1360000'+str(i)
            user.mobile='1360000'+str(i)
            user.password='1360000'+str(i)
            user.create_time = datetime.datetime(now.year, random.randint(1, 6), random.randint(1, now.day))
            user_list.append(user)
        db.session.add_all(user_list)
        db.session.commit()


# 钩子函数,验证管理员的登录
@admin_blueprint.before_request
def before_request():
    admin = UserInfo.query.get(session['admin_id']) if session.get('admin_id') else None
    if request.path != '/admin/login':
        if not admin:
            return redirect('/admin/login')
    g.user = admin

# 管理员登录页面
@admin_blueprint.route('/login',methods=['GET','POST'])
def login():

    # 登录页面的展示
    if request.method == 'GET':
        return render_template('admin/login.html')

    # 登录请求
    elif request.method == 'POST':

        # 获取参数
        mobile,password = request.form.get('mobile'),request.form.get('password')

        # 验证
        if not all((mobile,password)):
            abort(404)

        user = UserInfo.query.filter(UserInfo.mobile==mobile,UserInfo.isAdmin==True).first()

        if not user:
            return render_template('admin/login.html',error_info='用户名输入错误',mobile=mobile,password=password)

        if not user.check_pwd(password):
            return render_template('admin/login.html',error_info='密码输入错误',mobile=mobile,password=password)


        # 执行
        session['admin_id'] = user.id

        return redirect('/admin')

@admin_blueprint.route('/logout',methods=['POST'])
def logout():
    session.pop('admin_id')
    return jsonify(info='退出成功')

# 管理员主页
@admin_blueprint.route('/')
def index():
    return render_template('admin/index.html')


# 用户统计
@admin_blueprint.route('/user_count')
def user_count():
    now = datetime.datetime.now()
    # 显示数据
    # 1. 用户总数
    total_user = UserInfo.query.filter(UserInfo.isAdmin!=True).count()

    # 2. 用户月增新数
    month_register = UserInfo.query.filter(UserInfo.isAdmin!=True,UserInfo.create_time>=datetime.datetime(now.year,now.month,1)).count()

    # 3.用户日增新数
    day_register = UserInfo.query.filter(UserInfo.isAdmin!=True,UserInfo.create_time>=datetime.datetime(now.year,now.month,now.day)).count()

    # 4. 用户登录活跃数
    name = 'active%d%d%d'%(now.year,now.month,now.day)
    active_list = [int(i.decode()) for i in current_app.redis_client.hvals(name)]



    return render_template("admin/user_count.html",total_user=total_user,month_register=month_register,day_register=day_register,active_list=active_list)

# 用户列表
@admin_blueprint.route('/user_list')
def user_list():
    page = int(request.args.get('page',1))
    pagination = UserInfo.query.paginate(page,9,False)
    user_list = pagination.items
    total_page = pagination.pages
    return render_template("admin/user_list.html",user_list=user_list,page=page,total_page=total_page)

# 新闻审核
@admin_blueprint.route('/news_review')
def news_review():
    return render_template("admin/news_review.html")

# 新闻版式编辑
@admin_blueprint.route('/news_edit')
def news_edit():
    return render_template("admin/news_edit.html")

# 新闻分类管理
@admin_blueprint.route('/news_type')
def news_type():
    return render_template("admin/news_type.html")

