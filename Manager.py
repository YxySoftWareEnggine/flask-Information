import flask
from werkzeug.routing import BaseConverter
import flask_sqlalchemy


InformationApp  = flask.Flask(__name__)

class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


InformationApp.config.from_object(Config)
db= flask_sqlalchemy.SQLAlchemy(InformationApp)


if __name__ == '__main__':
    InformationApp.run()