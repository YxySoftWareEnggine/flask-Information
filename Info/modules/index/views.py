from . import index_blu
from Info import redis_store
import logging
from flask import current_app
import flask

@index_blu.route("/")
def index():
    return flask.render_template('index.html')

@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file("news/favicon.ico")