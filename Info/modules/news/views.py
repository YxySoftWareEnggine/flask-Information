
from . import news_blu
from Info import redis_store
import logging
from flask import current_app,g
import flask
from Info.models import User
from Info.models import News,Category
from Info import response_code
from ...utls.common import user_login_data


@news_blu.route("/<int:news_id>")
@user_login_data
def news_detail(news_id):
    user = g.user
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(6)
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []

    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
            "user": user.to_dict() if user else None,
            "news_dict_li": news_dict_li

    }
    return flask.render_template('news/detail.html', user_data=data)