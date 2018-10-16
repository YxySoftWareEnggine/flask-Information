#工具类
import logging
from flask import current_app
import flask
from Info.models import User
from Info.models import News,Category
import functools
from flask import g


index_dict ={
    "0":"first",
    "1":"second",
    "2":"third"
}


def to_index_class(index):

    for key,value in index_dict.items():
        if str(index) == key:
            return value
    return ""

def user_login_data(f):
    @functools.wraps(f)
    def wrapper(*args,**kwargs):
        user_id = flask.session.get("user_id", None)
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)

        news_list = []
        try:
            news_list = News.query.order_by(News.clicks.desc()).limit(6)
        except Exception as e:
            current_app.logger.error(e)

        g.user = user

        return f(*args,**kwargs)
    return wrapper