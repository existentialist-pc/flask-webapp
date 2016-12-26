from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager


class Role(db.Model):  # 用户类别类，适用于>2种用户类别的拓展。
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)  # .Column.Integer属性方法并未自动匹配，原因是它们搜索获自sqlalchemy包
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')  # 该表某数据与User表内哪些数据具有关联性

    def __repr__(self):
        return '<Role: %s>' % self.name


class User(db.Model, UserMixin):  # UserMixin为该类添加用户状态判断的方法。
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # 定义该数据的外键关联性，该列关联roles.id

    def __repr__(self):
        return '<User: %s>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter  # 设置password的时候调用？
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):  # 该password为常规password，hash过程由check_password_hash封装
        return check_password_hash(self.password_hash, password)  # 注意，第二个参数是未hash的参数！！


@login_manager.user_loader  # 这个修饰@意义是什么？
def load_user(user_id):  # 找到用户便返回该用户User对象
    return User.query.get(int(user_id))