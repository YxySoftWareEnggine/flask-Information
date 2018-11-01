from . import admin_blu
from Info import redis_store,db
import logging
from flask import current_app,g
import flask
from Info.models import User
from Info.models import News,Category,Comment
from Info import response_code
from ...utls.common import user_login_data
from ...utls import Yunstorage
from ...constants import *
from Info import db
from datetime import datetime,timedelta
import time






@admin_blu.route('/news_type',methods=["GET","POST"])
def new_type():

    if flask.request.method == "GET":
        category_li = []
        category= None
        try:
            category = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)

        for cate in category:
            category_li.append(cate.to_dict())
        data = {
            "category":category_li
        }
        return flask.render_template('admin/news_type.html',data=data)
    else:
        name = flask.request.json.get("name")
        id  = flask.request.json.get("id")

        if not name:
            return flask.jsonify(error=response_code.RET.DATAERR,errmsg="参数错误")

        if id:
            try:
                category = Category.query.filter(Category.id == id).first()
                category.name = name
                db.session.add(category)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(e)

            return flask.jsonify(errno=response_code.RET.OK,errmsg="成功")
        else:
            try:
                category = Category()
                category.name = name
                db.session.add(category)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(e)

            return flask.jsonify(errno=response_code.RET.OK, errmsg="成功")


@admin_blu.route('/new_edit_detail',methods=["GET","POST"])
def new_edit_detail():

    if flask.request.method == "GET":
        news_id = flask.request.args.get("news_id")

        try:
            news_id = int(news_id)
        except Exception as e:
            current_app.logger.error(e)

        news = News.query.get(news_id)

        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return flask.render_template('admin/news_edit_detail.html', errmsg="查询数据错误")

        category_dict_li = []
        for category in categories:
            # 取到分类的字典
            cate_dict = category.to_dict()
            # 判断当前遍历到的分类是否是当前新闻的分类，如果是，则添加is_selected为true
            if category.id == news.category_id:
                cate_dict["is_selected"] = True
            category_dict_li.append(cate_dict)

        # 移除最新的分类
        category_dict_li.pop(0)

        data = {
            "news":news.to_dict(),
            "category_dict_li":category_dict_li
        }
        return flask.render_template('admin/news_edit_detail.html',data= data)

    else:
        news_id = flask.request.form.get("news_id")
        title = flask.request.form.get("title")
        digest = flask.request.form.get("digest")
        content = flask.request.form.get("content")
        index_image = flask.request.files.get("index_image")
        category_id = flask.request.form.get("category_id")
        # 1.1 判断数据是否有值
        if not all([title, digest, content, category_id]):
            return flask.jsonify(errno=response_code.RET.PARAMERR, errmsg="参数有误")

        # 查询指定id的
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return flask.jsonify(errno=response_code.RET.DBERR, errmsg="数据查询失败")

        if not news:
            return flask.jsonify(errno=response_code.RET.NODATA, errmsg="未查询到新闻数据")

        # 1.2 尝试读取图片
        if index_image:
            try:
                index_image = index_image.read()
            except Exception as e:
                current_app.logger.error(e)
                return flask.jsonify(errno=response_code.RET.PARAMERR, errmsg="参数有误")

            # 2. 将标题图片上传到七牛
            try:
                key = Yunstorage.Stroge(index_image)
            except Exception as e:
                current_app.logger.error(e)
                return flask.jsonify(errno=response_code.RET.THIRDERR, errmsg="上传图片错误")
            news.index_image_url = QINIU_DOMIN_PREFIX + key

        # 3. 设置相关数据
        news.title = title
        news.digest = digest
        news.content = content
        news.category_id = category_id

        return flask.jsonify(errno=response_code.RET.OK, errmsg="OK")


@admin_blu.route('/new_edit',methods=["GET","POST"])
def new_edit():
    page = flask.request.args.get("p", 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    total_page = 1
    current_page = 1
    news = []

    try:
        item = News.query.filter().paginate(page, ADMIN_NEWS_PAGE_MAX_COUNT, False)
        news = item.items
        current_page = item.page
        total_page = item.pages
    except Exception as e:
        current_app.logger.error(e)
    news_dict = []

    for new_list in news:
        news_dict.append(new_list.to_review_dict())

    data = {
        "news_list": news_dict,
        "current_page": current_page,
        "total_page": total_page
    }
    return flask.render_template('admin/news_edit.html', data=data)



@admin_blu.route('/new_detail',methods=["GET","POST"])
def new_detail():

    if flask.request.method == "GET":
        news_id = flask.request.args.get("news_id")
        news = None
        try:
            news_id = int(news_id)
        except Exception as e:
            current_app.logger.error(e)

        try:
            news = News.query.filter(News.id == news_id).first()
        except Exception as e:
            current_app.logger.error(e)


        data = {
            "news":news.to_dict()
        }
        return flask.render_template('admin/news_review_detail.html',data=data)
    else:
        news_id = flask.request.json.get("news_id")
        action = flask.request.json.get("action")

        # 2.判断参数
        if not all([news_id, action]):
            return flask.jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")
        if action not in ("accept", "reject"):
            return flask.jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")

        news = None
        try:
            # 3.查询新闻
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)

        if not news:
            return flask.jsonify(errno=response_code.RET.NODATA, errmsg="未查询到数据")

        # 4.根据不同的状态设置不同的值
        if action == "accept":
            news.status = 0
        else:
            # 拒绝通过，需要获取原因
            reason = flask.request.json.get("reason")
            if not reason:
                return flask.jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")
            news.reason = reason
            news.status = -1

        # 保存数据库
        try:
            db.session.add(news)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return flask.jsonify(errno=response_code.RET.DBERR, errmsg="数据保存失败")
        return flask.jsonify(errno=response_code.RET.OK, errmsg="操作成功")

@admin_blu.route('/news_review',methods=["GET","POST"])
@user_login_data
def news_review():
    page = flask.request.args.get("p",1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    user = g.user
    total_page = 1
    current_page = 1
    news = []

    try:
        item = News.query.filter().paginate(page,ADMIN_NEWS_PAGE_MAX_COUNT,False)
        news = item.items
        current_page = item.page
        total_page = item.pages
    except Exception as e:
        current_app.logger.error(e)
    news_dict=[]

    for new_list in news:
        news_dict.append(new_list.to_review_dict())

    data ={
        "news_list":news_dict,
        "current_page":current_page,
        "total_page":total_page
    }
    return flask.render_template('admin/news_review.html',data=data)




@admin_blu.route('/user_list',methods=["GET","POST"])
@user_login_data
def user_list():
    page = flask.request.args.get("p", 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 设置变量默认值
    users = []
    current_page = 1
    total_page = 1

    # 查询数据
    try:
        paginate = User.query.filter(User.is_admin == False).order_by(User.last_login.desc()).paginate(page,
                                                                                                       ADMIN_USER_PAGE_MAX_COUNT,                                                                                             False)
        users = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    # 将模型列表转成字典列表
    users_list = []
    for user in users:
        users_list.append(user.to_admin_dict())

    context = {"total_page": total_page, "current_page": current_page, "users": users_list}
    return flask.render_template('admin/user_list.html',
                           data=context)


@admin_blu.route('/count',methods = ["GET","POST"])
@user_login_data
def user_count():
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 月新增数
    mon_count = 0
    t = time.localtime()
    begin_mon_date_str = '%d-%02d-01' % (t.tm_year, t.tm_mon)
    # 将字符串转成datetime对象
    begin_mon_date = datetime.strptime(begin_mon_date_str, "%Y-%m-%d")
    try:
        mon_count = User.query.filter(User.is_admin == False, User.create_time > begin_mon_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 日新增数
    day_count = 0
    begin_day_date = datetime.strptime(('%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)), "%Y-%m-%d")
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > begin_day_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 拆线图数据

    active_time = []
    active_count = []

    # 取到今天的时间字符串
    today_date_str = ('%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday))
    # 转成时间对象
    today_date = datetime.strptime(today_date_str, "%Y-%m-%d")

    for i in range(0, 31):
        # 取到某一天的0点0分
        begin_date = today_date - timedelta(days=i)
        # 取到下一天的0点0分
        end_date = today_date - timedelta(days=(i - 1))
        count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                  User.last_login < end_date).count()
        active_count.append(count)
        active_time.append(begin_date.strftime('%Y-%m-%d'))

    # User.query.filter(User.is_admin == False, User.last_login >= 今天0点0分, User.last_login < 今天24点).count()

    # 反转，让最近的一天显示在最后
    active_time.reverse()
    active_count.reverse()

    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_time": active_time,
        "active_count": active_count
    }

    return flask.render_template('admin/user_count.html', data=data)


@admin_blu.route('/index',methods=["GET","POST"])
@user_login_data
def index():
    user = g.user
    if not user:
        return flask.render_template('admin/login.html', errmsg="用户不存在")
    return flask.render_template('admin/index.html', user=user.to_dict())

@admin_blu.route('/login',methods=["GET","POST"])
def login():

    if flask.request.method == "GET":
        user_id = flask.session.get("user_id", None)
        is_admin = flask.session.get("is_admin", False)
        # 如果用户id存在，并且是管理员，那么直接跳转管理后台主页
        if user_id and is_admin:
            return flask.redirect(flask.url_for('admin.index'))
        return flask.render_template('admin/login.html')


    name = flask.request.form.get("username")
    password = flask.request.form.get("password")

    if not all([name,password]):
        return flask.render_template('admin/login.html',errmsg="参数错误")

    try:
        user = User.query.filter(User.mobile == name).first()
    except Exception as e:
        current_app.logger.error(e)
        return flask.render_template('admin/login.html', errmsg="用户不存在")

    if not user.check_passowrd(password):
        return flask.render_template('admin/login.html', errmsg="密码错误")

    if not user.is_admin:
        return flask.render_template('admin/login.html', errmsg="用户权限错误")

    flask.session["user_id"] = user.id
    flask.session["nick_name"] = user.nick_name
    flask.session["mobile"] = user.mobile
    flask.session["is_admin"] = True

    return flask.redirect(flask.url_for("admin.index"))














