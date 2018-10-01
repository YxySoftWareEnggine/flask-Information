from . import index_blu
from Info import redis_store
import logging
import flask

@index_blu.route("/")
def index():
    return flask.render_template('index.html')