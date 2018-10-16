import redis
import logging

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
    LOG_LEVEL = logging.DEBUG


class Developerment(Config):
    """开发环境配置"""
    DEBUG = True



class Production(Config):
    """生产环境配置"""
    DEBUG = False


class Testing(Config):
    DEBUG = True
    TESTING = True


config = {
    "development":Developerment,
    "testing":Testing,
    "Product":Production
}