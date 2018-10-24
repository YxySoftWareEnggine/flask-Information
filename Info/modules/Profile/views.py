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
