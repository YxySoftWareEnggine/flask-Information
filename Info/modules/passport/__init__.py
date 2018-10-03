from flask import Blueprint

passport_blu = Blueprint("passport", __name__, template_folder='templates', static_folder="static",url_prefix="/passport")

from . import views