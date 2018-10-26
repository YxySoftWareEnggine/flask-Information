from . import Profile_blu
from Info import redis_store,db
import logging
from flask import current_app,g
import flask
from Info.models import User
from Info.models import News,Category,Comment
from Info import response_code
from ...utls.common import user_login_data
from ...utls import Yunstorage
from ...constants import *
from Info import db
from datetime import datetime



@Profile_blu.route('/news_list',methods=["GET","POST"])
@user_login_data
def news_list():
    p = flask.request.args.get("p", 1)
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        p = 1

    user = g.user
    news_li = []
    current_page = 1
    total_page = 1
    try:
        paginate = News.query.filter(News.user_id == user.id).paginate(p, USER_COLLECTION_MAX_NEWS, False)
        # 获取当前页数据
        news_li = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []

    for news_item in news_li:
        news_dict_li.append(news_item.to_review_dict())
    data = {"news_list": news_dict_li, "total_page": total_page, "current_page": current_page}
    return flask.render_template('news/user_news_list.html', data=data)


@Profile_blu.route('/release_news',methods=["GET","POST"])
@user_login_data
def release_info():
    user = g.user
    if flask.request.method == "GET":
        category = Category.query.all()
        category_filter = []
        for categ in category:
            category_filter.append(categ.to_dict())
        category_filter.pop(0)
        data = {
            "user_info": category_filter
        }
        return flask.render_template('news/user_news_release.html',user_data = data)

    News_Title = flask.request.form.get("News_Title")
    Summary = flask.request.form.get("Summary")
    News_Image = flask.request.files.get("News_Image").read()
    content = flask.request.form.get("content1")
    category_id = flask.request.form.get("category_id")

    if not all([News_Title,Summary,News_Image,content,category_id]):
        return flask.jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")

    try:
        new = News()
        new.title = News_Title
        new.content = content
        new.digest = Summary
        new.create_time = datetime.now()
        new.index_image_url = QINIU_DOMIN_PREFIX+Yunstorage.Stroge(News_Image)
        new.source = "个人用户"
        new.user_id = user.id
        new.category_id = category_id
        new.status = 1
        db.session.add(new)
        db.session.commit()

    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return flask.jsonify(errno=response_code.RET.DBERR, errmsg="保存数据失败")

    return flask.jsonify(errno=response_code.RET.OK, errmsg="发布成功，等待审核")



@Profile_blu.route('/collection_info',methods=["GET","POST"])
@user_login_data
def collection_info():
    p = flask.request.args.get("p", 1)
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        p = 1

    user = g.user
    collections = []
    current_page = 1
    total_page = 1
    try:
        # 进行分页数据查询
        paginate = user.collection_news.paginate(p, USER_COLLECTION_MAX_NEWS, False)
        # 获取分页数据
        collections = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    # 收藏列表
    collection_dict_li = []
    for news in collections:
        collection_dict_li.append(news.to_basic_dict())

    data = {"total_page": total_page, "current_page": current_page, "collections": collection_dict_li}
    return flask.render_template('news/user_collection.html', data=data)



@Profile_blu.route('/pass_info',methods=["GET","POST"])
@user_login_data
def pass_info():
    user = g.user
    if flask.request.method == "GET":
        data = {
            "user_info":user.to_dict()
        }
        return flask.render_template('news/user_pass_info.html',user_data = data)

    CurrentPass =flask.request.json.get("CurrentPass")
    NewPass = flask.request.json.get("NewPass")
    ConfimPass = flask.request.json.get("ConfimPass")

    if user.check_passowrd(CurrentPass):
        try:
            user.password = NewPass
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
        return flask.jsonify(errno=response_code.RET.OK, errmsg="成功")
    return flask.jsonify(errno=response_code.RET.DATAERR, errmsg="密码错误")

@Profile_blu.route('/pic_info',methods=["GET","POST"])
@user_login_data
def Pic_info():
    user = g.user
    if flask.request.method == "GET":
        data = {
            "user_info":user.to_dict()
        }
        return flask.render_template('news/user_pic_info.html',user_data = data)

    Image = flask.request.files.get('avatar').read()

    url = Yunstorage.Stroge(Image)

    try:
        user.avatar_url = url
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)

    return flask.jsonify(errno=response_code.RET.OK, errmsg="OK",data ={"avatar_url": QINIU_DOMIN_PREFIX + url})


@Profile_blu.route('/user_base_info',methods=["GET","POST"])
@user_login_data
def base_info():
    user = g.user
    if flask.request.method == "GET":
        data ={
            "name":user.nick_name,
            "signature": user.signature if user.signature else ""
        }
        return flask.render_template('news/user_base_info.html',user_data = data)

    signature = flask.request.json.get("signature")
    nick_name = flask.request.json.get("nick_name")
    gender = flask.request.json.get("gender")

    if not all([signature,nick_name,gender]):
        return flask.jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")

    try:
        user.signature = signature
        user.nick_name = nick_name
        user.gender = gender

        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
    return flask.jsonify(errno=response_code.RET.OK, errmsg="成功")




@Profile_blu.route('/info',methods=["GET","POST"])
@user_login_data
def user_info():
    user = g.user
    if not user:
        flask.redirect('/')
    data = {
        "user":user.to_dict()
    }
    return flask.render_template('news/user.html', user_data=data)
