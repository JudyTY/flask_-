from flask import Blueprint, render_template, session, request, jsonify, abort, current_app
from models import UserInfo, NewsCategory, NewsInfo, db,NewsComment

views_blueprint = Blueprint('views', __name__)


# 首页视图
@views_blueprint.route('/')
def index():
    # 用户
    user = UserInfo.query.get(session['user_id']) if session.get('user_id') else ''

    # 点击排行
    news_list = NewsInfo.query.order_by(NewsInfo.click_count.desc())[0:6]

    # 返回新闻分类列表
    category_list = NewsCategory.query.all()

    return render_template('news/index.html', user=user, title='首页-新经资讯', category_list=category_list,
                           news_list=news_list)


# 返回首页新闻json数据
@views_blueprint.route('/index_data')
def index_data():
    page = int(request.args.get('page', 1))

    # 分页显示
    category_id = int(request.args.get('category_id', '0'))

    pagination = (NewsInfo.query.filter_by(category_id=category_id) if category_id else NewsInfo.query).order_by(
        NewsInfo.update_time.desc()).paginate(page, 4, False)

    news_list = []

    for news in pagination.items:
        news_list.append({
            'id': news.id,
            "pic_url": news.pic_url,
            'title': news.title,
            'summary': news.summary,
            'user_id': news.user_id,
            "user_name": news.user.nick_name,
            "user_pic_url": news.user.avatar_url,
            "update_time": news.update_time
        })

    return jsonify(page=page, news_list=news_list)


# 展示新闻详情页
@views_blueprint.route('/<int:news_id>')
def detail(news_id):
    # 用户
    user = UserInfo.query.get(session['user_id']) if session.get('user_id') else ''

    # 点击排行
    news_list = NewsInfo.query.order_by(NewsInfo.click_count.desc())[0:6]

    # 获取新闻对象
    news = NewsInfo.query.get(news_id)

    # 如果没有此新闻对象,抛出404错误,并结束函数
    if not news:
        abort(404)
        return

    # 如果不是发布此新闻的用户点击,则新闻的点击数加1
    if user != news.user:
        news.click_count +=1
        db.session.commit()

    return render_template('news/detail.html', user=user, news_list=news_list, news=news)


# 收藏新闻
@views_blueprint.route('/collect', methods=['POST'])
def news_collect():

    user = UserInfo.query.get(session['user_id']) if session.get('user_id') else None

    # 验证
    # 1. 判断用户是否登录
    if not user:
        return jsonify(login=1)

    news_id = int(request.form.get('news_id','0'))

    # 判断是收藏操作还是取消收藏操作,默认是0----收藏操作
    action = int(request.form.get('action','0'))

    # 2. 验证是否传了正确的新闻
    if not news_id:
        # request.remote_addr获得用户ip
        current_app.logger_xjzx.info('  from---/collect has a Non-normal request-------' + request.remote_addr)
        return jsonify(Non_normal='bad_request')

    news = NewsInfo.query.get(news_id)

    # 3. 判断news对象是否存在以及用户是不是已经收藏过此新闻(用于阻拦非正常请求)
    if (news not in user.news_collect) if action else (news in user.news_collect) or not news:
        current_app.logger_xjzx.info(' Non-normal request-------' + request.remote_addr)
        return jsonify(Non_normal='bad_request')

    # 提交数据库
    try:
        user.news_collect.remove(news)  if action else user.news_collect.append(news)
        db.session.commit()
        return jsonify(success_info='操作成功')
    except:
        return jsonify(error_info='服务器出错')


# 评论
@views_blueprint.route('/comment',methods=['GET','POST'])
def comment():
    user_id = session.get('user_id') or 0

    # get请求做数据返回操作
    if request.method == 'GET':
        news = NewsInfo.query.get(int(request.args.get('news_id','0')))
        comment_list = []

        # 剔除评论的回复
        for comment in news.comments.filter_by(comment_id=None).order_by(NewsComment.create_time.desc()):

            # 查询评论的回复数据
            reply_list = []
            for comment_reply in comment.comments:
                reply_list.append({
                    'nick_name':comment_reply.user.nick_name,
                    'msg':comment_reply.msg
                })
            comment_list.append({
                'is_like':1 if comment.id in [int(comment_id) for comment_id in current_app.redis_client.lrange('likecomments%d'%user_id,0,-1)] else None,
                'id':comment.id,
                'user_avatar_url':comment.user.avatar_url,
                'nick_name':comment.user.nick_name,
                'msg':comment.msg,
                # strftime可以将日期格式化
                'create_time':comment.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'reply_list':reply_list,
                'like_count':comment.like_count
            })
        return jsonify(comment_list=comment_list,comment_count=news.comment_count)

    # post请求做添加评论对象操作
    elif request.method == 'POST':

        dict1 = request.form
        news_id = int(dict1.get('news_id'))
        msg=dict1.get('msg')

        # 验证
        # 1. 如果数据不完整显示提示消息
        if not all((news_id,msg)):
            return jsonify(error_info='数据不完整')


        news = NewsInfo.query.get(news_id)
        user = UserInfo.query.get(session['user_id'])

        # 2.如果非正常请求,记录客户端ip
        if not all((user, news)):
            current_app.logger_xjzx.info('from---/comment--has a Non-normal request-------' + request.remote_addr)
            return jsonify(Non_normal='bad_request')

        # 添加评论对象
        comment = NewsComment()
        comment.news_id = news_id
        comment.user_id = user.id
        comment.msg = msg
        # 操作成功后,新闻的评论数加1
        news.comment_count+=1

        try:
            db.session.add(comment)
            db.session.commit()
            return jsonify(success_info='操作成功')
        except:
            return jsonify(error_info='服务器出错')


# 完善粉丝数,发表数
@views_blueprint.route('/reset')
def reset():
    user_list = UserInfo.query.all()
    for user in user_list:
        user.public_count = user.news.count() if user.news.count() else 0
        user.follow_count = user.follow_user.count() if user.follow_user.count() else 0
        db.session.commit()
    return 'all set!'

# 回复评论
@views_blueprint.route('/comment/reply',methods=['POST'])
def comment_reply():
    # 获取登录用户id
    user = UserInfo.query.get(session['user_id']) if session.get('user_id') else None
    # 未登录返回登录
    if not user:
        return jsonify(login=1)

    # 获取数据
    dict1 = request.form
    news = NewsInfo.query.get(int(dict1.get('news_id')))
    newscomment = NewsComment.query.get(int(dict1.get('comment_id')))
    msg = dict1.get('msg')

    # 如果没有新闻对象或者评论对象,视为非正常请求
    if not all((news,newscomment)):
        current_app.logger_xjzx.info(' from---/comment_comments has a Non-normal request-------' + request.remote_addr)
        return jsonify(Non_normal='bad_request')

    # 添加评论的评论对象
    comment = NewsComment()
    comment.news_id = news.id
    comment.user_id = user.id
    comment.comment_id = newscomment.id
    comment.msg = msg
    # 评论后news的评论数+1
    news.comment_count+=1
    db.session.add(comment)
    db.session.commit()

    return jsonify(success_info='评论成功')

# 评论点赞
@views_blueprint.route('/comment/up',methods=['POST'])
def comment_up():
    user = UserInfo.query.get(session['user_id']) if session.get('user_id') else None
    if not user:
        return jsonify(login=1)

    comment = NewsComment.query.get(request.form.get('comment_id'))

    action = request.form.get('action',0)

    if not comment or (comment.id in [int(comment_id) for comment_id in current_app.redis_client.lrange('likecomments%d'%user.id,0,-1)]) if action=='1' else (comment.id not in [int(comment_id) for comment_id in current_app.redis_client.lrange('likecomments%d'%user.id,0,-1)]):
        current_app.logger_xjzx.info(' from---/comment/up has a Non-normal request-------' + request.remote_addr)
        return jsonify(Non_normal='bad_request')

    if action=='1':
        comment.like_count+=1
        current_app.redis_client.rpush('likecomments%d'%user.id,comment.id)
    else:
        comment.like_count-=1
        current_app.redis_client.lrem('likecomments%d' % user.id,0 ,comment.id)

    # 使用redis数据库记录点赞(将redis配置在app文件中)

    db.session.commit()
    return jsonify(success_info='操作成功',like_count=comment.like_count)

# 关注和取消关注
@views_blueprint.route('/follow',methods=['POST'])
def follow():

    user = UserInfo.query.get(session['user_id']) if session.get('user_id') else None
    if not user:
        return jsonify(login=1)

    follow_user_id = request.form.get('follow_user_id')
    follow_user = UserInfo.query.get(follow_user_id)
    action = request.form.get('action')

    if not follow_user or follow_user in user.follow_user:
        current_app.logger_xjzx.info(' from---/comment/up has a Non-normal request-------' + request.remote_addr)
        return jsonify(Non_normal='bad_request')

    user.follow_user.append(follow_user) if action=='1' else user.follow_user.remove(follow_user)
    db.session.commit()
    return jsonify(success_info="操作成功")


# 登录后获取收藏,点赞,关注情况
@views_blueprint.route('/status',methods=['POST'])
def status():
    user = UserInfo.query.get(session['user_id']) if session.get('user_id') else None
    news_id = str(request.form.get('news_id'))[1:]
    if not all((news_id,user)):
        abort(404)

    news = NewsInfo.query.get(news_id)
    # 获取收藏新闻状态
    is_collect = 1 if news in user.news_collect else None

    # 获取关注状态
    is_follow = 1 if UserInfo.query.get(news.user_id) in user.follow_user else None
    like_list = []
    for comment in news.comments:
        if comment.id in [int(comment_id) for comment_id in current_app.redis_client.lrange('likecomments%d'%user.id,0,-1)]:
            like_list.append(comment.id)
    print(like_list)
    return jsonify(is_collect=is_collect,is_follow=is_follow,like_list=like_list)





