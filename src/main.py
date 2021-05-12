#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from pathlib import Path

from flask import Flask, render_template, Response, redirect, url_for,\
    request, session, abort, send_from_directory
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, \
    login_required, login_user, logout_user
import pymysql

# 本地内部引用
import lsb

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

# 判断是否为管理员 现阶段直接以 user_id 是否为1 来判断
def is_admin(user_id):
    return 1 if user_id == 1 else 0

@app.route('/')
@login_required
def home():  # some protected url
    return render_template("dashboard.html", manager=is_admin(current_user.id))

@app.route("/login", methods=["GET", "POST"])
def login():
    # somewhere to login
    if request.method == 'POST':
        login_info = request.form.to_dict()
        user = User.query.filter_by(name=login_info.get("username")).first()

        if user:
            if user.password == login_info.get("password"):
                login_user(user)
                print(f'用户登陆 {user.id} : {user.name}')
                return redirect("/")

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


@app.route("/upload", methods=["GET", "POST"])
@login_required
def mimi():  # 加密模块 - 使用密文加密
    if request.method == "POST":
        # 前期准备
        f = request.files['file']
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        user_id = current_user.id
        print(f'当前登陆用户id {user_id}')

        # 检测是否存在对应路径
        my_file = Path(f'{basepath}/static/uploads/{str(user_id)}mod')
        if my_file.is_dir():
            # 存在
            print(f'路径存在 {my_file}')
        else:
            # 不存在
            os.mkdir(my_file)  # 只能创建单级目录
            print(f'路径不存在 {my_file}')

        my_file = Path(f'{basepath}/static/uploads/{str(user_id)}')
        if my_file.is_dir():
            # 存在
            print(f'路径存在 {my_file}')
        else:
            # 不存在
            os.mkdir(my_file)  # 只能创建单级目录
            print(f'路径不存在 {my_file}')
        
        f.save(
            f'{basepath}/static/uploads/{str(user_id)}/{secure_filename(f.filename)}')
        print("保存成功")

        post_info = request.form.to_dict()
        # 获取加密参数
        secret_text = post_info.get("secret")
        # 获取原照片路径
        src_img_path = f'{basepath}/static/uploads/{str(user_id)}/{secure_filename(f.filename)}'
        # 获取处理后照片路径
        mod_img_path = f'{basepath}/static/uploads/{str(user_id)}mod/{secure_filename(f.filename)}'
        print(secret_text, src_img_path, mod_img_path)

        lsb.jiami(secret_text, src_img_path, mod_img_path)
        # 展示加密后结果
        return render_template("upload_result.html", mod_img_path=secure_filename(f.filename))

    return render_template("upload.html")


@app.route("/jiemi", methods=["GET", "POST"])
@login_required
def demi():
    # 解密模块 根据数据文件名称,查询自身服务器资源
    if request.method == "POST":
        # 前期准备
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        user_id = current_user.id
        print(f'当前登陆用户id {user_id}')

        # 获取提交数据
        post_info = request.form.to_dict()    
        # 加密图像路径
        # mod_img_path = post_info.get("mod_img_path")
        mod_img_path = f'{basepath}/static/uploads/{str(user_id)}mod/{post_info.get("mod_img_path")}.bmp'
        
        secret_text = lsb.jiemi(mod_img_path)
        print(secret_text)

        return render_template("/jiemi_result.html", secret_text=secret_text)
    return render_template("jiemi.html")


@app.route("/jiemi2", methods=["GET", "POST"])
@login_required
def demi2():
    # 解密模块 用户亲自上传文件
    if request.method == "POST":
        # 前期准备
        f = request.files['file']
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        user_id = current_user.id
        print(f'当前登陆用户id {user_id}')

        # 检测是否存在对应路径
        my_file = Path(f'{basepath}/static/uploads/{str(user_id)}self')
        if my_file.is_dir():
            # 存在
            print(f'路径存在 {my_file}')
        else:
            # 不存在
            os.mkdir(my_file)  # 只能创建单级目录
            print(f'路径不存在 {my_file}')

        mod_img_path = f'{basepath}/static/uploads/{str(user_id)}self/{secure_filename(f.filename)}'
        f.save(mod_img_path)
        secret_text = lsb.jiemi(mod_img_path)

        return render_template("/jiemi_result.html", secret_text=secret_text)
    return render_template("jiemi2.html")


@app.route("/tip/<mod_img_path>")
@login_required
def tip(mod_img_path):
    # 展示上传并加密后的图片
    return app.send_static_file(f"uploads/{current_user.id}mod/{mod_img_path}")


@app.route("/download/<mod_img_path>")
@login_required
def download(mod_img_path):
    # 展示加密图片 提供下载
    basepath = os.path.dirname(__file__)  # 当前文件所在路径
    return send_from_directory(f"{basepath}/static/uploads/{current_user.id}mod", filename=mod_img_path, as_attachment=True)


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
