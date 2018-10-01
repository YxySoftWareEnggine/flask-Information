import flask
import flask_script
import flask_migrate
from Config import Config
import Info


app = Info.Create_app("development")
Info.set_up("development")
manager = flask_script.Manager(app)
flask_migrate.Migrate(app,Info.db)
manager.add_command('db',flask_migrate.MigrateCommand)

@app.route('/')
def index():
    flask.session['names'] = 'yangXY'
    return '111111'

if __name__ == '__main__':
    manager.run()