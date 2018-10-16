from flask import Blueprint

index_blu = Blueprint("index", __name__, template_folder='templates', static_folder="static")

from . import views