from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from flask import current_app  # 获取当前app的相关配置信息
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

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
    confirmed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User: %s>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter  # 设置password的时候调用？
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):  # 该password为常规password，hash过程由check_password_hash封装
        return check_password_hash(self.password_hash, password)  # 注意，check_password_hash()第二个参数才是未hash的参数！！

    def generate_confirmation_token(self):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=3600)
        return s.dumps({'confirm':self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])  # 验证不需要获得expires_in信息
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

@login_manager.user_loader  # 该@下定义回调函数。函数固定为传递id为参数，获得user类实例或none。
# 该回调函数在reload_user时执行 => user_id从session['user_id']获得，ctx = _request_ctx_stack.top  ctx.user = 该函数返回实例对象
def load_user(user_id):
    return User.query.get(int(user_id))
