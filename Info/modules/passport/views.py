from . import passport_blu
from Info import redis_store
import logging
from flask import current_app
import flask
from Info import constants
from Info import response_code
from Info.utls.captcha.captcha import captcha
import json
import re
import random
from Info.ThirdLibs.yuntongxun.sms import CCP
from Info.models import User
from Info import db
import datetime

@passport_blu.route('/logout',methods=["GET"])
def logout():
    flask.session.pop("user_id")
    flask.session.pop("nick_name")
    flask.session.pop("mobile")
    flask.session.pop("is_admin")

    return flask.jsonify(errno=response_code.RET.OK, errmsg="成功")


@passport_blu.route('/log',methods=["POST"])
def log():
    params_dict = flask.request.json
    mobile = params_dict.get("mobile")
    password = params_dict.get("password")

    try:
        result=User.query.filter_by(mobile=mobile).first()
        logging.debug(result)
    except Exception as e:
        return flask.jsonify(errno=response_code.RET.DATAERR, errmsg="数据查询错误")
    if result.check_passowrd(password):
        flask.session["user_id"] = result.id
        flask.session["nick_name"] = result.nick_name
        flask.session["mobile"] = result.mobile
        flask.session["is_admin"] = False
        # 记录用户最后一次登录时间
        result.last_login = datetime.datetime.now()
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
        return flask.jsonify(errno=response_code.RET.OK, errmsg="成功")
    else:
        return flask.jsonify(errno=response_code.RET.DATAERR, errmsg='密码输入错误')



@passport_blu.route('/register',methods=["POST"])
def register():
    params_dict = flask.request.json
    mobile = params_dict.get("mobile")
    smscode = params_dict.get("smscode")
    password = params_dict.get("password")

    if not all([mobile,smscode,password]):
        return flask.jsonify(errno=response_code.RET.PARAMERR,errmsg="参数错误")

    try:
        real_sms_code = redis_store.get("SMS_"+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return flask.jsonify(errno=response_code.RET.DATAERR, errmsg="数据查询错误")
    if not real_sms_code:
        return flask.jsonify(errno=response_code.RET.NODATA,errmsg="短信验证码已过期")
    if real_sms_code.decode("utf-8")!=smscode:
        return flask.jsonify(errno=response_code.RET.DATAERR,errmsg="验证码输入错误")

    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    user.last_login = datetime.datetime.now()
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return flask.jsonify(errno=response_code.RET.DATAERR,errmsg="数据添加错误")

    flask.session["user_id"] = user.id
    flask.session["mobile"] = user.mobile
    flask.session["nick_name"] = user.nick_name
    flask.session["admin"] = False

    return  flask.jsonify(errno=response_code.RET.OK, errmsg="成功")


@passport_blu.route('/sms_code',methods=['POST'])
def send_sms_code():

    paramdict = flask.request.json
    mobile = paramdict.get("mobile")
    image_code = paramdict.get("image_code")
    image_code_id = paramdict.get("image_code_id")


    if not all([mobile,image_code,image_code_id]):
        return flask.jsonify(errno=response_code.RET.PARAMERR,errmsg="参数错误")
    if not re.match('1[35678]\\d{9}',mobile):
        return flask.jsonify(errno=response_code.RET.PARAMERR,errmsg="参数错误")

    try:
        real_image_code = redis_store.get("ImageCodeId"+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return flask.jsonify(errno=response_code.RET.DATAERR,errmsg="数据查询错误")

    if not real_image_code:
        return flask.jsonify(errno=response_code.RET.NODATA,errmsg="图片验证码已过期")

    if real_image_code.upper()!=real_image_code.upper():
        return flask.jsonify(errno=response_code.RET.DATAERR,errmsg="验证码输入错误")

    sms_code_str = "%06d"%random.randint(0,999999)
    current_app.logger.debug("验证码输入内容:%s"%sms_code_str)
    CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES / 60], "1")

    try:
        redis_store.set("SMS_"+mobile,sms_code_str)
    except Exception as e:
        logging.debug(e)

    return flask.jsonify(errno=response_code.RET.OK, errmsg="成功")


@passport_blu.route("/image_code")
def get_image_code():
    image_code_id=flask.request.args.get("imageCodeId",None)

    if not image_code_id:
        return flask.abort(403)

    name,text,image=captcha.generate_captcha()

    try:
        redis_store.set("ImageCodeId"+image_code_id,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        flask.abort(500)

    response=flask.make_response(image,())
    response.headers["Content-Type"] = "image/jpg"
    return image




