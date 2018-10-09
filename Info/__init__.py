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
from Config import Config,config
import logging
import logging.handlers as handle
from flask_wtf.csrf import generate_csrf

db = flask_sqlalchemy.SQLAlchemy()
redis_store = None #type = redis.StrictRedis

def set_up(config_name):
    logging.basicConfig(level=config[config_name].LOG_LEVEL)
    file_log_handler = handle.RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def Create_app(config_name):

    InformationApp  = flask.Flask(__name__)

    InformationApp.config.from_object(config[config_name])

    db.init_app(InformationApp)

    from .utls.common import to_index_class

    InformationApp.add_template_filter(to_index_class,"index_class")

    global redis_store
    redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST,port=config[config_name].REDIS_PORT)

    flask_wtf.CSRFProtect(InformationApp)

    @InformationApp.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        response.set_cookie("csrf_token",csrf_token)
        return response
    flask_session.Session(app=InformationApp)

    from Info.modules.index import index_blu

    InformationApp.register_blueprint(index_blu)

    from Info.modules.passport import passport_blu

    InformationApp.register_blueprint(passport_blu)

    from Info.modules.news import news_blu

    InformationApp.register_blueprint(news_blu)

    return InformationApp

