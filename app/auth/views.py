from . import auth
from .form import LoginForm
from ..models import User
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required


@auth.route('/login', methods=['GET', 'POST'])  # 集成登录渲染与登录验证功能，并未分离。
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid Email or Password.')
    return render_template('/auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))  # 试试跳到最近的无需登录页面

