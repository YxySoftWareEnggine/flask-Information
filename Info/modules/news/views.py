
from . import news_blu
from Info import redis_store
import logging
from flask import current_app,g
import flask
from Info.models import User
from Info.models import News,Category
from Info import response_code
from ...utls.common import user_login_data



@news_blu.route('/news_comment',methods=["POST"])
@user_login_data
def news_comment():
    user = g.user
    if not user:
        return flask.jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")

    news_id = flask.request.json.get("news_id")
    comment = flask.request.json.get("comment")
    parent_id = 

@news_blu.route('/news_collect',methods = ["POST"])
@user_login_data
def news_collect():

    user = g.user
    if not user:
        return flask.jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")

    news_id=flask.request.json.get("news_id")
    action=flask.request.json.get("action")

    if not all([news_id,action]):
        return flask.jsonify(errno=response_code.RET.DATAERR, errmsg="参数错误")

    if action not in ["collect","cancel_collect"]:
        return flask.jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
    news = None

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return flask.jsonify(errno=response_code.RET.DATAERR, errmsg="数据查询错误")

    if action == "cancel_collect":
        if news in user.collection_news:
            user.collection_news.remove(news)
    else:
        if news not in user.collection_news:
            user.collection_news.append(news)

    return flask.jsonify(errno=response_code.RET.OK, errmsg="成功")


@news_blu.route("/<int:news_id>")
@user_login_data
def news_detail(news_id):
    user = g.user
    news_list = []
    new = None
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(6)
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []

    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    try:
        new = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not new:
        flask.abort(404)

    new.clicks+=1

    is_collected = True

    if user:
        if new in user.collection_news:
            is_collected=True
        else:
            is_collected=False

    data = {
            "user": user.to_dict() if user else None,
            "news_dict_li": news_dict_li,
            "news":new.to_dict(),
            "is_collected":is_collected
    }
    return flask.render_template('news/detail.html', user_data=data)