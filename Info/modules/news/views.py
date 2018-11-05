
from . import news_blu
from Info import redis_store,db
import logging
from flask import current_app,g
import flask
from Info.models import News,Category,Comment,CommentLike,User,tb_user_follows
from Info import response_code,db
from ...utls.common import user_login_data


@news_blu.route('/news_follow',methods=["POST"])
@user_login_data
def new_follow():

    follow = flask.request.json.get("follow")
    cid = flask.request.json.get("cid")
    user = User.query.get(cid)
    if follow:
        if user in g.user.followers:
            return flask.jsonify(errno=response_code.RET.DATAERR, errmsg="用户已关注")
        else:
            try:
                user.followers.append(g.user)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(e)
            return flask.jsonify(errno=response_code.RET.OK, errmsg="OK")
    else:
        try:
            user.followers.remove(g.user)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
        return flask.jsonify(errno=response_code.RET.OK, errmsg="OK")

@news_blu.route('/news_commentLike',methods=["POST"])
@user_login_data
def news_commentlike():

    user = g.user
    if not user:
        return flask.jsonify(errno=response_code.RET.SESSIONERR, errmsg="用户未登录")
    comment_id = flask.request.json.get("comment_id")
    action = flask.request.json.get("action")

    comment = Comment.query.get(int(comment_id))


    if not all([comment_id,action]):
        return flask.jsonify(errno=response_code.RET.PARAMERR, errmsg="参数不足")
    if action=="add":
        try:

            commentLike = CommentLike()
            commentLike.comment_id = int(comment_id)
            commentLike.user_id = int(user.id)
            if comment.like_count==1:
                return flask.jsonify(errno=response_code.RET.DATAERR, errmsg="只能点一次赞")
            comment.like_count+=1
            db.session.add(commentLike)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return flask.jsonify(errno=response_code.RET.DBERR, errmsg="存储失败")
        return flask.jsonify(errno=response_code.RET.OK, errmsg="评论成功")

    elif action == "delete":
        try:
            comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=g.user.id).first()
            if comment_like:
                db.session.delete(comment_like)
                # 减小点赞条数
                comment.like_count-=1
                db.session.commit()
        except Exception as e:
            return flask.jsonify(errno=response_code.RET.DBERR, errmsg="存储失败")
        return flask.jsonify(errno=response_code.RET.OK, errmsg="评论成功")


@news_blu.route('/news_comment',methods=["POST"])
@user_login_data
def news_comment():
    user = g.user
    if not user:
        return flask.jsonify(errno=response_code.RET.SESSIONERR, errmsg="用户未登录")

    news_id = flask.request.json.get("news_id")
    comment = flask.request.json.get("comment")
    action= flask.request.json.get("action")
    parent_id = flask.request.json.get("parent_id")

    if not all([news_id,comment]):
        return flask.jsonify(errno=response_code.RET.PARAMERR, errmsg="参数不足")

    comment_str = Comment()
    comment_str.user_id = user.id
    comment_str.news_id = news_id
    comment_str.content = comment

    if parent_id:
        comment_str.parent_id = parent_id

    try:
        db.session.add(comment_str)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return flask.jsonify(errno=response_code.RET.DBERR, errmsg="存储失败")

    data = {
        "comment":comment_str.to_dict()
    }
        # 返回响应
    return flask.jsonify(errno=response_code.RET.OK, errmsg="成功",data=data)


@news_blu.route('/news_collect',methods = ["POST"])
@user_login_data
def news_collect():

    user = g.user
    if not user:
        return flask.jsonify(errno=response_code.RET.SESSIONERR, errmsg="用户未登录")

    news_id=flask.request.json.get("news_id")
    action=flask.request.json.get("action")

    if not all([news_id,action]):
        return flask.jsonify(errno=response_code.RET.DATAERR, errmsg="参数错误")

    if action not in ["collect","cancel_collect"]:
        return flask.jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
    news = None

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return flask.jsonify(errno=response_code.RET.DATAERR, errmsg="数据查询错误")

    if action == "cancel_collect":
        if news in user.collection_news:
            user.collection_news.remove(news)
    else:
        if news not in user.collection_news:
            user.collection_news.append(news)
            db.session.commit()

    return flask.jsonify(errno=response_code.RET.OK, errmsg="成功")


@news_blu.route("/<int:news_id>")
@user_login_data
def news_detail(news_id):
    user = g.user
    news_list = []
    new = None
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(6)
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []

    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    try:
        new = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not new:
        flask.abort(404)

    new.clicks+=1

    is_collected = True

    if user:
        if new in user.collection_news:
            is_collected=True
        else:
            is_collected=False

    comments = None
    try:
        comments = Comment.query.filter(Comment.news_id==news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    comment_list = []
    for item in comments if comments else []:
        comments_dict = item.to_dict()
        comment_list.append(comments_dict)

    resp_dict = new.to_dict()

    count = None
    follow = None
    if resp_dict["author"]:
        count = News.query.filter(News.user_id == resp_dict["author"]["id"]).count()
        user = User.query.get(resp_dict["author"]["id"])
        if user in g.user.followed:
            follow = True
        else:
            follow = False

    final_data = {
        "user": user.to_dict() if user else None,
        "news_dict_li": news_dict_li,
        "news": new.to_dict(),
        "is_collected": is_collected,
        "comments": comment_list,
        "Count":count,
        "is_follow":follow
    }

    return flask.render_template('news/detail.html', user_data=final_data)