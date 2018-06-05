# app对象
from app import Create_app
# 配置
from config import Developconfig
# 拓展命令
from flask_script import Manager
# db对象
from models import db
# 迁移
from flask_migrate import Migrate, MigrateCommand

app = Create_app(Developconfig)

if __name__ == '__main__':
    manager = Manager(app)
    migrate = Migrate(app, db)

    # 添加数据库迁移命令
    manager.add_command('db', MigrateCommand)

    # 添加创建管理员用户的拓展命令
    from views_admin import CreateAdmin,CreateUser
    manager.add_command('createadmin',CreateAdmin)

    # 添加创建多条用户的命令
    manager.add_command('createuser',CreateUser)

    manager.run()

