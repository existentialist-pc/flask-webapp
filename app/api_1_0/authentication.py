from flask import jsonify, g  # 在不使用flask_login，无current_user时可以使用g程序上下文保存用户信息
from flask_httpauth import HTTPBasicAuth
from ..models import AnonymousUser, User
from .errors import unauthorized, forbidden
from . import api

auth = HTTPBasicAuth()


@auth.verify_password   # http认证回调
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True  # 注意！这里认为是匿名用户依然返回True，即可以通过auth.login_required验证，返回False则不会通过！
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None  # 简练！
    user = User.query.filter_by(email= email_or_token).first()
    g.token_used = False
    if not user:
        return False
    g.current_user = user
    return user.verify_password(password)  # 找用户，验证密码


@auth.error_handler  # 认证出错401 error_handler自定义
def auth_error():  # 401 认证错误
    return unauthorized('Invalid credentials')


@api.before_request  # 针对api请求
@auth.login_required  # 要求登录(verify_password返回True)才能使用api。注意！如果取消该@，则不会运行@auth.verify_password修饰函数！g.current_user也不存在，会报错！
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('Unconfirmed accout')


@api.route('/token')  # 根据用户信息决定是否访问
@auth.login_required
def generate_token():  # 要验证才能访问到
    if g.token_used or g.current_user.is_anonymous:
        return unauthorized('Invalid credentials')
    return jsonify({'id':g.current_user.id,
                    'token':g.current_user.generate_confirmation_token(expiration=3600).decode('ascii'),
                    'expiration':3600})







