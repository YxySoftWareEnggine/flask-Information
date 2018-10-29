import flask
import flask_script
import flask_migrate
from Config import Config
import Info
from Info import models,constants
from Info.models import User
from Info import db

app = Info.Create_app("development")
Info.set_up("development")
manager = flask_script.Manager(app)
flask_migrate.Migrate(app,Info.db)
manager.add_command('db',flask_migrate.MigrateCommand)


@manager.option("-n",'-name',dest='name')
@manager.option('-p','-password',dest='password')
def Create_adminUser(name,password):
    user = User()
    user.mobile = name
    user.nick_name = name
    user.password = password
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
        print("创建成功")
    except Exception as e:
        print(e)
        db.session.rollback()



if __name__ == '__main__':
    manager.run()