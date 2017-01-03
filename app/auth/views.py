from . import auth
from .form import LoginForm, RegisterForm
from .. import db
from ..models import User
from ..email import send_email
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
# 这里导入的current_user类似上下文的方法，注意该变量也是不需要在render_template中即可传递的。


@auth.route('/login', methods=['GET', 'POST'])  # 集成登录渲染与登录验证功能，并未分离
def login():
    form = LoginForm()
    if form.validate_on_submit(): # 此处以内判断不生效逻辑也可以参考RegisterForm内验证函数设计，归入LoginForm类中。选择看灵活性与清晰性需求
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('无效的邮箱地址或密码！')
    return render_template('/auth/login.html', form=form)

@auth.route('/logout')
@login_required  # flask_login提供的登录验证
def logout():
    logout_user()
    flash('您已登出')
    return redirect(url_for('main.index'))  # 试试跳到最近的无需登录页面


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()  # 生成验证hash码
        send_email(user.email, '确认用户注册', 'auth/email/confirm', token=token, user=user)
        flash('您已注册登录,请保持登录状态，并60分钟内在注册邮箱确认激活！')
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')  # 注意这里的token，也是send_email()中作为key的token => url_for('auth.confirm', token=...)
@login_required  # 保证登录用户的存在，current_user存在
def confirm(token):
    if current_user.confirmed:
        flash('您已经成功激活，无需再激活')
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('成功激活，%s,欢迎回来' % current_user.username)
    else:
        flash('激活失效，尝试重新激活')
    return redirect(url_for('main.index'))


@auth.before_app_request  # 获取请求权限前执行，类似middleware
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':  # request.endpoint为Flask定义，为视图函数名
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')  # 可以做成api，与register中发送确认功能重叠。跳转逻辑交给前端
@login_required
def send_confirm():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '确认用户注册', 'auth/email/confirm', token=token, user=current_user)
    flash('您已发送邮箱验证请求，请保持登录状态，并60分钟内在注册邮箱确认激活！')
    return redirect(url_for('main.index'))









