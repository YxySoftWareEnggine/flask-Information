import flask
from werkzeug.routing import BaseConverter
import flask_sqlalchemy
import redis
import flask_wtf
import flask_session
import base64
import os
import flask_script
import flask_migrate

InformationApp  = flask.Flask(__name__)
manager = flask_script.Manager(InformationApp)

class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    SECRET_KEY = "dsftregrwegrtrhregthryyuikuooiregtrhyjt"
    SESSION_TYPE = 'redis'
    SESSION_USE_SIGNER = 'True'
    SESSION_REDIS = redis.StrictRedis(REDIS_HOST,REDIS_PORT)
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 86400*2



InformationApp.config.from_object(Config)
db= flask_sqlalchemy.SQLAlchemy(InformationApp)
redis_store = redis.StrictRedis(Config.REDIS_HOST,Config.REDIS_PORT)
flask_wtf.CSRFProtect(InformationApp)
flask_session.Session(app=InformationApp)
flask_migrate.Migrate(InformationApp,db)
manager.add_command('db',flask_migrate.MigrateCommand)

@InformationApp.route('/')
def index():
    flask.session['names'] = 'yangXY'
    return '111111'


if __name__ == '__main__':
    manager.run()