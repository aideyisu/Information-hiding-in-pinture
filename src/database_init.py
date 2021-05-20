import time
import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)

class Config(object):
    """配置参数"""
    # 设置连接数据库的URL
    user = 'root'
    password = '123456'
    database = 'mfz'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@127.0.0.1:3306/%s' % (user,password,database)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@127.0.0.1:3306/%s' % ("root","123456","test")
    # 设置sqlalchemy自动更跟踪数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 查询时会显示原始SQL语句
    app.config['SQLALCHEMY_ECHO'] = True
    # 禁止自动提交数据处理
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False

# 读取配置
app.config.from_object(Config)

# 创建数据库sqlalchemy工具对象
db = SQLAlchemy(app)

class User(db.Model):
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
        self.password = password
        self.status = 0

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



if __name__ == '__main__':
    # 删除所有表
    db.drop_all()
    # 创建所有表
    db.create_all()

    # 创建20个默认用户
    # create some users with ids 1 to 20
    for i in range(1, 21):
        id = i
        name = "user" + str(id)
        phone = id
        password = name + "pw"
        db.session.add(User(name, phone, password))
        db.session.commit()
        
    for i in range(1,15):
        db.session.add(Loghis(i, 0))
        db.session.commit()
        time.sleep(3)

    for i in range(1,15):
        db.session.add(Loghis(i, 0))
        db.session.commit()
        time.sleep(3)

    for i in range(1,13):
        db.session.add(Operate(i, 1, "lsb", f"test{i}.png", 0, ""))
        db.session.commit()

    for i in range(1,13):
        db.session.add(Operate(i, 2, "lsb", f"test{i}.png", 0, ""))
        db.session.commit()   
    #    def __init__(self, uid, op_type, sec_type, filename, op_result, fail_source):
