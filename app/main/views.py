from . import main
from .forms import NameForm, EditProfileForm
from .. import db
from ..models import User
from flask import render_template, abort, flash, redirect, url_for
from flask_login import login_required, current_user


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


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


from ..decorators import admin_required, permission_required
from ..models import Permission

@main.route('/admin')
@admin_required
def for_admins_only():
    return "For administrators!"


@main.route('/moderator')
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"