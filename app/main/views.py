from . import main
from .forms import PostForm, EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import User, Role, Post, Permission
from flask import render_template, abort, flash, redirect, url_for
from flask_login import login_required, current_user
from ..decorators import admin_required


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(content=form.content.data, auth=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()  # 类.列属性.desc() 传入排序函数
    return render_template('index.html', form=form, posts = posts)


@main.route('/user/<username>')
def user(username):  # 此页面可被非该用户查看
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('个人资料已经成功更新')
        return redirect(url_for('main.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile-admin/<int:id>', methods=['GET', 'POST'])  # 要传递被修改用户对象，这里用id传递
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user)  # 传递user用于验证修改与否
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)  # SelectField这里传递的是int数值
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('id:%s, %s的个人资料已经成功修改' % (user.id, user.username))
        return redirect(url_for('main.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id or Role.query.filter_by(default=True).first().id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)  # 共用模板


from ..decorators import permission_required


@main.route('/admin')
@admin_required
def for_admins_only():
    return "For administrators!"


@main.route('/moderator')
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"