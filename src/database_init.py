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
    # 定义表名
    __tablename__ = 'users'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(64), unique=True, index=True)
    phone = db.Column(db.String(64),unique=True)
    # email = db.Column(db.String(64),unique=True)
    password = db.Column(db.String(64))
    # role_id = db.Column(db.Integer, db.ForeignKey('roles.id')) # 设置外键
    def __init__(self, name, phone, password):
        self.name = name
        self.phone = phone
        self.password = password

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


