from . import passport_blu
from Info import redis_store
import logging
from flask import current_app
import flask
from Info import constants
from Info.utls.captcha.captcha import captcha

@passport_blu.route('/sms_code',methods=['POST'])
def send_sms_code():






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

    response=flask.make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response




