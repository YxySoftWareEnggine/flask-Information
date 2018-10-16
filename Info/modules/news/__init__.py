from flask import blueprints

news_blu = blueprints.Blueprint("news", __name__, template_folder='templates', static_folder="static",url_prefix="/news")

from . import views
