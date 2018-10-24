from flask import Blueprint

Profile_blu = Blueprint("Profile", __name__, template_folder='templates', static_folder="static",url_prefix='/user')

from . import views