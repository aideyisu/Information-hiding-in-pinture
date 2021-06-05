#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import datetime
import hashlib
from pathlib import Path

from flask import Flask, render_template, Response, redirect, url_for,\
    request, session, abort, send_from_directory
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, \
    login_required, login_user, logout_user

import pymysql
pymysql.install_as_MySQLdb()

# 本地内部引用
import lsb
import site_jiami
import site_jiemi

# 罪恶的全局变量
all_method = ["lsb", "site"]

app = Flask(__name__, static_folder="static")

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
    status = db.Column(db.Integer, index=True)  # 账户状态 0 为正常 -1 为被管理员删除
    # role_id = db.Column(db.Integer, db.ForeignKey('roles.id')) # 设置外键

    def __init__(self, name, phone, password):
        # self.id = id
        self.name = name
        self.phone = phone
        temp_password = hashlib.sha256()
        temp_password.update(password.encode('utf-8'))
        self.password = temp_password.hexdigest()
        self.status = 0

    def __repr__(self):
        return "%d/%s/%s/%s" % (self.id, self.name, self.phone, self.password)

class Loghis(db.Model):
    # 定义表名
    __tablename__ = 'loghis'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    # 用户id
    uid = db.Column(db.Integer, index=True)
    # 登陆是否成功 (0成功 1失败)
    succ = db.Column(db.Integer, index=True)
    # 操作时间
    ctime = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, uid, succ):
        self.uid = uid
        self.succ = succ


class Operate(db.Model):
    # 定义表名
    __tablename__ = 'oparate'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 用户id
    uid = db.Column(db.Integer, index=True)
    # 操作类型 （1上传源图片 2从服务端解密 3上传加密图片解密）
    op_type = db.Column(db.Integer, index=True)
    # 加解密方式
    sec_type = db.Column(db.String(64), index=True)
    # 操作具体名称
    type_name = db.Column(db.String(64), index=True)
    # 相关文件名
    filename = db.Column(db.String(64), index=True)
    # 操作结果 (0成功 非0失败)
    op_result = db.Column(db.Integer, index=True)
    # 失败原因
    fail_source = db.Column(db.String(64), index=True)
    # 操作时间
    ctime = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, uid, op_type, sec_type, filename, op_result, fail_source):
        self.uid = uid
        self.op_type = op_type
        self.sec_type = sec_type
        if op_type == 1:
            # 上传原图
            self.type_name = "upload source picture"
        elif op_type == 2:
            # 服务端解密
            self.type_name = "server decode"
        elif op_type == 3:
            # 上传解密
            self.type_name = "upload decode"
        else:
            # 尚未定义 undefined
            self.type_name = "undefined"
        self.filename = filename
        self.op_result = op_result
        self.fail_source = fail_source


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
            temp_password = hashlib.sha256()
            temp_password.update(login_info.get("password").encode('utf-8'))
            uplodde_password = temp_password.hexdigest()
            if user.password == uplodde_password:
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

def register_add_user(username, phone,  password):
    #  注册普通用户
    db.session.add(User(username, phone, password))
    db.session.commit()

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
        post_info = request.form.to_dict()
        f = request.files['file']
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        user_id = current_user.id
        print(f'当前登陆用户id {user_id}')

        # 获取选择的加密手法
        secret_method = post_info.get("sec_method")
        print(f'选择的加密手法为 {secret_method}')

        # 获取加密参数
        secret_text = post_info.get("secret")

        mod_img_path = ""
        if secret_method == "lsb":
            # 检测是否存在对应路径
            my_file = Path(f'{basepath}/static/uploads/{str(user_id)}mod')
            if not my_file.is_dir():
                # 不存在
                os.mkdir(my_file)  # 只能创建单级目录
                print(f'路径不存在 {my_file}')

            my_file = Path(f'{basepath}/static/uploads/{str(user_id)}')
            if not my_file.is_dir():
                # 不存在
                os.mkdir(my_file)  # 只能创建单级目录
                print(f'路径不存在 {my_file}')

            f.save(
                f'{basepath}/static/uploads/{str(user_id)}/{secure_filename(f.filename)}')
            print("保存成功")

            # 获取原照片路径
            src_img_path = f'{basepath}/static/uploads/{str(user_id)}/{secure_filename(f.filename)}'
            # 获取处理后照片路径
            mod_img_path = f'{basepath}/static/uploads/{str(user_id)}mod/{secure_filename(f.filename)}'
            print(secret_text, src_img_path, mod_img_path)

            lsb.jiami(secret_text, src_img_path, mod_img_path)
        elif secret_method == "site":
            # 检测是否存在对应路径
            my_file = Path(f'{basepath}/static/uploads/{str(user_id)}site')
            if not my_file.is_dir():
                # 不存在
                os.mkdir(my_file)  # 只能创建单级目录
                print(f'路径不存在 {my_file}')

            # TODO res.png优化
            # 获取处理后照片路径
            mod_img_path = f'{basepath}/'
            # 实际存储位置
            save_path = f'static/uploads/{str(user_id)}site/res.png'
            site_jiami.site_jiami(secret_text, save_path)
        else:
            pass
            # TODO 其他加密解密方案

        # 记录行为记录
        db.session.add(Operate(user_id, 1, secret_method,
                               secure_filename(f.filename), 0, ""))
        db.session.commit()
        return render_template("upload_result.html", mod_img_path=secure_filename(f.filename), method=secret_method)

    # TODO 获取全部方法

    return render_template("upload.html", all_method=all_method)


@app.route("/jiemi", methods=["GET", "POST"])
@login_required
def demi():
    # 解密模块 根据数据文件名称,查询自身服务器资源
    if request.method == "POST":
        # 前期准备
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        user_id = current_user.id
        print(f'当前登陆用户id {user_id}')
        secret_text = ""
        # 获取提交数据
        post_info = request.form.to_dict()

        # 获取选择的加密手法
        secret_method = post_info.get("sec_method")
        print(f'选择的加密手法为 {secret_method}')


        if secret_method == "lsb":
            # 加密图像路径
            # mod_img_path = post_info.get("mod_img_path")
            mod_img_path = f'{basepath}/static/uploads/{str(user_id)}mod/{post_info.get("mod_img_path")}.bmp'
            # 记录行为记录
            db.session.add(
                Operate(user_id, 2, "none", post_info.get("mod_img_path")+".bmp", 0, ""))
            db.session.commit()
            secret_text = lsb.jiemi(mod_img_path)
        elif secret_method == "site":
            # 加密图像路径
            mod_img_path = f'{basepath}/static/uploads/{str(user_id)}site/{post_info.get("mod_img_path")}.png'

            secret_text = site_jiemi.site_jiemi(mod_img_path)
        else:
            pass
            # TODO 其他加密解密方案
        print(secret_text)

        return render_template("/jiemi_result.html", secret_text=secret_text)

    return render_template("jiemi.html", all_method=all_method)


@app.route("/jiemi2", methods=["GET", "POST"])
@login_required
def demi2():
    # 解密模块 用户亲自上传文件
    if request.method == "POST":
        # 前期准备
        post_info = request.form.to_dict()
        succ = 1
        secret_text = ""
        f = request.files['file']
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        user_id = current_user.id
        print(f'当前登陆用户id {user_id}')

        # 检测是否存在对应路径
        my_file = Path(f'{basepath}/static/uploads/{str(user_id)}self')
        if not my_file.is_dir():
            # 不存在
            os.mkdir(my_file)  # 只能创建单级目录
            print(f'路径不存在 {my_file}')

        # 获取选择的加密手法
        secret_method = post_info.get("sec_method")
        print(f'选择的加密手法为 {secret_method}')

        if secret_method == "lsb":
            # 检测是否存在对应路径
            my_file = Path(f'{basepath}/static/uploads/{str(user_id)}self/lsb')
            if not my_file.is_dir():
                # 不存在
                os.mkdir(my_file)  # 只能创建单级目录
                print(f'路径不存在 {my_file}')

            mod_img_path = f'{basepath}/static/uploads/{str(user_id)}self/lsb/{secure_filename(f.filename)}'
            f.save(mod_img_path)

            secret_text = lsb.jiemi(mod_img_path)
        elif secret_method == "site":
            # 检测是否存在对应路径
            my_file = Path(f'{basepath}/static/uploads/{str(user_id)}self/site')
            if not my_file.is_dir():
                # 不存在
                os.mkdir(my_file)  # 只能创建单级目录
                print(f'路径不存在 {my_file}')

            mod_img_path = f'{basepath}/static/uploads/{str(user_id)}self/site/{secure_filename(f.filename)}'
            f.save(mod_img_path)

            secret_text = site_jiemi.site_jiemi(mod_img_path)
        else:
            pass
            # TODO 其他加密解密方案

        if len(secret_text) < 100 and len(secret_text) != 0:
            print("似乎对了")
            succ = 0
        print("疑似长度为", len(secret_text))

        # 记录行为记录
        db.session.add(Operate(user_id, 3, "none", secure_filename(f.filename), 0, ""))
        db.session.commit()

        return render_template("/jiemi_result.html", secret_text=secret_text, succ=succ, method = secret_method)
    return render_template("jiemi2.html",  all_method=all_method)


@app.route("/tip/<method>/<mod_img_path>")
@login_required
def tip(method, mod_img_path):
    # 展示上传并加密后的图片

    # return app.send_static_file(f"uploads/{current_user.id}site/{mod_img_path}")
    if method == "lsb":
        return app.send_static_file(f"uploads/{current_user.id}mod/{mod_img_path}")
    else:
        return app.send_static_file(f"uploads/{current_user.id}site/res.png")


@app.route("/download/<mod_img_path>")
@login_required
def download(mod_img_path):
    # 展示加密图片 提供下载
    basepath = os.path.dirname(__file__)  # 当前文件所在路径
    return send_from_directory(f"{basepath}/static/uploads/{current_user.id}mod",path=mod_img_path , filename=mod_img_path, as_attachment=True)

@app.route("/download_site")
@login_required
def download_site():
    # 展示加密图片 提供下载
    basepath = os.path.dirname(__file__)  # 当前文件所在路径
    return send_from_directory(f"{basepath}/static/uploads/{current_user.id}site", path="res.png" , filename="res.png", as_attachment=True)


@app.route("/history")
@login_required
def history_list():
    # history list
    # 历史操作记录
    uid = current_user.id
    # 检测是否存在对应路径,读取list
    history_operate_list = Operate.query.filter_by(uid=uid).all()

    for item in history_operate_list:
        print(item)
        print(item.type_name)
    return render_template("history_list.html",history_operate_list = history_operate_list, uid=uid)

@app.route("/history_m")
@login_required
def history_listm():
    # history list
    # 历史操作记录
    uid = current_user.id
    # 检测是否存在对应路径,读取list
    history_operate_list = Operate.query.all()

    return render_template("history_list_m.html",history_operate_list = history_operate_list)


@app.route("/loging_history")
@login_required
def login_list():
    # login history list
    uid = current_user.id
    # 检测是否存在对应路径,读取list
    # history_login_list = Loghis.query.filter_by(uid=uid).all()
    history_login_list = Loghis.query.all()
    return render_template("login_list.html",history_login_list = history_login_list, uid=uid)


@app.route("/manager_user", methods=["GET", "POST"])
@login_required
def manager_user():
    # 判断是否为管理员账户
    user_id = current_user.id
    if not is_admin(user_id):
        return redirect("/")

    # 拉取全部用户信息进行展示
    all_info = User.query.filter(User.status == 0).all()

    if request.method == "POST":
        search_info = request.form.to_dict()

        if search_info.get("newman"):
                # 新建用户
                db.session.add(User(search_info.get("newman"),
                                    search_info.get("newphone"),
                                    search_info.get("newpw"), 0))
                db.session.commit()
                print(f'成功添加用户 {search_info.get("newman")}')
        elif search_info.get("reid"):
            # 修改用户数据
            user = User.query.get(search_info.get("reid"))
            user.name = search_info.get("rename")
            user.phone = int(search_info.get("rephone"))
            # 密码sha-256处理
            temp_password = hashlib.sha256()
            temp_password.update(search_info.get("repw").encode('utf-8'))
            user.password = temp_password.hexdigest()
            # user.password = search_info.get("repw")
            db.session.commit()

        return redirect("/manager_user")

    return render_template("manager_user.html", all_info=all_info)

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
