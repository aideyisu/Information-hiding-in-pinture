#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, Response, redirect, url_for,\
    request, session, abort
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, \
    login_required, login_user, logout_user
import pymysql
pymysql.install_as_MySQLdb()


app = Flask(__name__, static_folder="static")
# PyClone 处理记录文件
open_file_name = "log_pyclone.txt"

# config
app.config.update(
    DEBUG=True,
    SECRET_KEY='secret_xxx'
)

# 这里登陆的是root用户，要填上自己的密码，MySQL的默认端口是3306，填上之前创建的数据库名jianshu,连接方式参考 \
# http://docs.sqlalchemy.org/en/latest/dialects/mysql.html
# mysql+pymysql://<username>:<password>@<host>/<dbname>[?<options>]
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1:3306/mfz'
# 设置sqlalchemy自动更跟踪数据库
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# 查询时会显示原始SQL语句
app.config['SQLALCHEMY_ECHO'] = True
# 禁止自动提交数据处理
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
# 创建SQLAlichemy实例
db = SQLAlchemy(app)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin, db.Model):
    # silly user model
    # 定义表名
    __tablename__ = 'users'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True, index=True)
    phone = db.Column(db.String(64), unique=True)
    # email = db.Column(db.String(64),unique=True)
    password = db.Column(db.String(64))
    # role_id = db.Column(db.Integer, db.ForeignKey('roles.id')) # 设置外键

    def __init__(self, name, phone, password):
        # self.id = id
        self.name = name
        self.phone = phone
        self.password = password

    def __repr__(self):
        return "%d/%s/%s/%s" % (self.id, self.name, self.phone, self.password)

@app.route('/')
@login_required
def home():  # some protected url
    return render_template("hello.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # somewhere to login
    if request.method == 'POST':
        login_info = request.form.to_dict()
        user = User.query.filter_by(name=login_info.get("username")).first()

        if user:  # 用户存在 且 密码相同
            if user.password == login_info.get("password"):
                login_user(user)
                print(f'用户登陆 {user.id} : {user.name}')
                return redirect("/history_list")

        return abort(401)
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    # somewhere to logout
    logout_user()
    return render_template("logout.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    # create new user
    if request.method == "POST":
        login_info = request.form.to_dict()
        # 新增用户
        register_add_user(login_info.get("username"), login_info.get(
            "phone"), login_info.get("password"))
        return redirect("/login")
        # return redirect(request.args.get("next"))
    else:
        return render_template("register.html")

# TODO 加密解密模块
@app.route("/mimi")
@login_required
def mimi():
    # TODO 加密解密
    return render_template("mimi.html")

@app.route("/demi")
@login_required
def demi():
    # TODO 解密模块
    return render_template("demi.html")

# TODO 数据(上传下载)模块

@app.errorhandler(401)
def page_not_found(e):
    # handle login failed
    return Response('<p>Login failed</p>')


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    user = User.query.get(userid)  # get为主键查询
    return user


if __name__ == "__main__":
    app.debug = True  # 开启快乐幼儿源模式
    app.run()



