from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_mail import Mail
from flask_login import LoginManager  # 页面登录相关

from flask import Flask
from config import config

db = SQLAlchemy()
bootstrap = Bootstrap()
moment = Moment()
mail = Mail()

login_manager = LoginManager()
login_manager.session_protection = 'strong'  # 强保护，检测用户的IP，代理变动等，异常即自动登出。
login_manager.login_view = 'auth.login'  # 设定登录页面端点,供url_for()查询？


def create_app(config_name):
    # 控制app运行的上下文环境。不create_app仍可以设置db、bootstrap等的执行逻辑，但依附于app的执行操作不会确实执行。
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)  # 思考作用,在上一步实现过了吧？

    db.init_app(app) # 开始为该app挂载各种与该模块相关的配置.config 与 属性方法等
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # blueprint注册
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')  # 前缀'/'，不后缀'/'

    return app