from . import db  # 属性db.Column类中default设置生效在写入数据库时，希望立即初始化，应在db.Model类__init__()设定属性
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from flask import current_app  # 获取当前app的相关配置信息
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
import hashlib
from flask import request
from markdown2 import markdown
import bleach


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text())
    content_html = db.Column(db.Text())
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def forge_posts(count=100):
        from random import seed, randint
        import forgery_py
        seed()
        user_count = User.query.count()
        for i in range(count):
            user = User.query.offset(randint(0,user_count-1)).first()
            post = Post(content=forgery_py.lorem_ipsum.sentences(randint(1,3)),
                        timestamp=forgery_py.date.date(True),
                        auth=user)
            db.session.add(post)
            db.session.commit()

    @staticmethod
    def on_changed_content(target, value, oldvalue, initiator):  # 回调函数
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong',
                        'ul', 'h1', 'h2', 'h3', 'p', 'br', 'hr']  # 'br'没就没换行, bleach过滤在markdown转化后
        target.content_html = bleach.clean(markdown(value), tags=allowed_tags, strip=True)



class Role(db.Model):  # 用户类别类，适用于>2种用户类别的拓展。
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)  # .Column.Integer属性方法并未自动匹配，原因是它们搜索获自sqlalchemy包
    name = db.Column(db.String(64), unique=True)
    permission = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False, index=True)  # 用于初始化User时的默认role设置，为True则为用户的默认role
    users = db.relationship('User', backref='role', lazy='dynamic')  # 该表某数据与User表内哪些数据具有关联性，传类名字符串

    def __repr__(self):
        return '<Role: %s>' % self.name

    @staticmethod
    def insert_roles():  # 该方法对所有该类实例只需要初始化执行一次
        roles = {
            'Administrator':(0xff, False),
            'Moderator':(Permission.MODERATE_COMMENTS|Permission.WRITE_ARTICLES|Permission.COMMENT|Permission.FOLLOW, False),
            'User':(Permission.WRITE_ARTICLES|Permission.COMMENT|Permission.FOLLOW, True)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if not role:
                role = Role(name=r)
            role.permission = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Follow(db.Model):  # 作为self-referential多对多关联表，要在User之前定义！foreign_key能找到
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)


class User(db.Model, UserMixin):  # UserMixin为该类添加用户状态判断的方法
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # 定义该数据的外键关联性，该列关联roles.id 实际数据库中表名
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))  # md5格式
    posts = db.relationship('Post', backref='auth', lazy='dynamic')
    comments = db.relationship('Comment', backref='auth', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')


    def __init__(self, **kwargs):  # 这样写要保证只有kw传递参数。省略了位置参数*args
        super(User, self).__init__(**kwargs)
        if self.role is None:  # 对各用户实例的role或role_id初始化
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permission=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

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

    def can(self, permissions):  # 判断中增加role要存在，进一步保证不出错
        return self.role is not None and (self.role.permission & permissions) == permissions

    def is_admin(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        if not self.avatar_hash:
            self.avatar_hash = hash
        return '%s/%s?s=%s&d=%s&r=%s' % (url, hash, size, default, rating)

    @staticmethod
    def forge_users(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()  # 初始化随机数生成器，防止生成规律的雷同性。如果每次seed()传入相同的参数，则在生成时会有相同的规律性
        for i in range(count):
            u = User(
                username=forgery_py.internet.user_name(True),
                email = forgery_py.internet.email_address(),
                password = forgery_py.lorem_ipsum.word(),
                confirmed = True,
                name = forgery_py.name.full_name(),
                location = forgery_py.address.city(),
                about_me=forgery_py.lorem_ipsum.sentence(),
                member_since = forgery_py.date.date(True)
            )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:  # unique错误
                db.session.rollback()

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None  # 获得的是Follow()对象

    def is_followed_by(self, user):
        return self.followers.filer_by(follower_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(followed=user,follower=self)  # 传递对象，自动获得对应的外键值;查询用id
            db.session.add(follow)
            db.session.commit()

    def unfollow(self, user):
        follow = self.followed.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id==Post.author_id).\
            filter(Follow.follower_id==self.id)  # filter指定类名！


class AnonymousUser(AnonymousUserMixin):  # 继承is_anonymous方法属性为True，为默认匿名用户类增加需要的属性方法

    def can(self, permissions):
        return False

    def is_admin(self):
        return False

login_manager.anonymous_user = AnonymousUser  # .anonymouse_user默认初始化为AnonymousUserMixin类。注意是类而不是实例


@login_manager.user_loader  # 该@下定义回调函数。函数固定为传递id为参数，获得user类实例或none。该内嵌的闭包关系到current_app
# 该回调函数在reload_user时执行 => user_id从session['user_id']获得，ctx = _request_ctx_stack.top  ctx.user = 该函数返回实例对象
def load_user(user_id):
    return User.query.get(int(user_id))


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text())
    content_html = db.Column(db.Text())
    disabled = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_content(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'li', 'ol', 'strong',
                        'ul', 'h1', 'p', 'br']
        target.content_html = bleach.clean(markdown(value), tags=allowed_tags, strip=True)

db.event.listen(Comment.content, 'set', Comment.on_changed_content)
db.event.listen(Post.content, 'set', Post.on_changed_content)  # SQLAlchemy提供事件监听回调，set就执行
