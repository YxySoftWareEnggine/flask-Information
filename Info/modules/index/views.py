from . import index_blu
from Info import redis_store
import logging

@index_blu.route("/")
def index():
    redis_store.set("name","yxy")
    logging.debug(redis_store.get("name"))
    return '111111'