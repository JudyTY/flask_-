from flask import Flask,render_template
from models import db
from views_news import views_blueprint
from views_user import user_blueprint
from views_admin import admin_blueprint
from flask.ext.wtf import CSRFProtect
from flask_session import Session
import redis



def Create_app(config):
    app = Flask(__name__)
    # 配置app
    app.config.from_object(config)
    db.init_app(app)
    # 注册蓝图
    app.register_blueprint(views_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(admin_blueprint)
    CSRFProtect(app)
    Session(app)

    import logging
    from logging.handlers import RotatingFileHandler
    # 设置日志的记录等级
    logging.basicConfig(level=logging.DEBUG)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler(config.BASE_DIR + "/logs/xjzx.log", maxBytes=1024 * 1024 * 100,
                                           backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
    app.logger_xjzx = logging

    # 配置redis
    host,port,redis_db=app.config.get('REDIS_HOST'),app.config.get('REDIS_PORT'),app.config.get('REDIS_DB')
    app.redis_client = redis.StrictRedis(host=host,port=port,db=redis_db)

    # 处理404错误
    @app.errorhandler(404)
    def e404(e):
        return render_template('news/404.html')
    return app
