from . import index_blu
from Info import redis_store
import logging
from flask import current_app
import flask
from Info.models import User
from Info.models import News
from Info import response_code



@index_blu.route("/news_list")
def news_list():
    cid = flask.request.args.get("cid", "1")
    page = flask.request.args.get("page", "1")
    per_page = flask.request.args.get("per_page", "10")

    # 2. 校验参数
    try:
        page = int(page)
        cid = int(cid)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return flask.jsonify(errno=response_code.RET.PARAMERR, errmsg="参数")

    filters = [News.status == 0]
    if cid != 1:
        filters.append(News.category_id == cid)
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return flask.jsonify(errno=flask.RET.DBERR, errmsg="数据查询错误")

    # 取到当前页的数据
    news_model_list = paginate.items  # 模型对象列表
    total_page = paginate.pages
    current_page = paginate.page

    # 将模型对象列表转成字典列表
    news_dict_li = []
    for news in news_model_list:
        news_dict_li.append(news.to_basic_dict())

    data = {"total_page": total_page, "current_page": current_page, "news_dict_li": news_dict_li}

    return flask.jsonify(errno=response_code.RET.OK, errmsg="OK", data=data)


@index_blu.route("/")
def index():
    user_id = flask.session.get("user_id", None)
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    news_list = []
    try:
        news_list=News.query.order_by(News.clicks.desc()).limit(6)
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []

    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
                "user": user.to_dict() if user else None,
                "news_dict_li":news_dict_li
            }
    return flask.render_template('index.html', user_data=data)



@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file("news/favicon.ico")
