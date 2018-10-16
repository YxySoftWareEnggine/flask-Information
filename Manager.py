import flask
import flask_script
import flask_migrate
from Config import Config
import Info
from Info import models,constants

app = Info.Create_app("development")
Info.set_up("development")
manager = flask_script.Manager(app)
flask_migrate.Migrate(app,Info.db)
manager.add_command('db',flask_migrate.MigrateCommand)


if __name__ == '__main__':
    manager.run()