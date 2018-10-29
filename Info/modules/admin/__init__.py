import flask
from flask import blueprints



admin_blu = blueprints.Blueprint("admin", __name__, template_folder='templates', static_folder="static",url_prefix="/admin")

from . import views

@admin_blu.before_request
def before_request():
    if not flask.request.url.endswith(flask.url_for("admin.login")):
        user_id = flask.session.get("user_id")
        is_admin = flask.session.get("is_admin", False)

        if not user_id or not is_admin:
                # 判断当前是否有用户登录，或者是否是管理员，如果不是，直接重定向到项目主页
            return flask.redirect('/')