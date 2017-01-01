from . import main
from .forms import PostForm, EditProfileForm, EditProfileAdminForm, CommentForm
from .. import db
from ..models import User, Role, Post, Permission, Follow, Comment
from flask import render_template, abort, flash, redirect, url_for, request, current_app, make_response
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(content=form.content.data, auth=current_user._get_current_object())  # auth要被赋予User对象本身，不是代理
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    page = request.args.get('page', 1, type=int)  # 从GET请求url中获取参数,’page‘为qs
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)  # 创建Post查询结果分页信息类，现在page页
    posts = pagination.items  # 类.列属性.desc() 传入排序函数
    return render_template('index.html', form=form, posts=posts, pagination=pagination, show_followed=show_followed)


@main.route('/all')  # 可以做api
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*3600)
    return resp

@main.route('/followed')  # 可以做api
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*3600)
    return resp


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)  # 合并404逻辑
    form = CommentForm()
    if current_user.can(Permission.COMMENT) and form.validate_on_submit():
        comment = Comment(content=form.content.data, post=post, auth=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('评论成功！')
        return redirect(url_for('main.post', id=post.id, page=1))  # 升序排列则定义返回page=-1，取最后一页。
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() / current_app.config['FLASKY_POSTS_PER_PAGE']) + 1
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form, comments=comments, pagination=pagination)


@main.route('/edit-post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.auth and not current_user.is_admin():
        return redirect(url_for('main.post', id=id))  # abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.content = form.content.data
        db.session.add(post)
        db.session.commit()
        flash('短文章已经更新')
        return redirect(url_for('main.post', id=id))
    form.content.data = post.content
    return render_template('edit_post.html',form=form)


@main.route('/user/<username>')
def user(username):  # 此页面可被非该用户查看
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/follow/<username>')
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('该用户不存在')
        abort(404)
    if current_user.is_following(user):
        flash('您已关注该用户，不用重复关注')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    flash('已成功关注%s' % user.username)
    return redirect(url_for('main.user', username=username))


@main.route('/unfollow/<username>')
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('该用户不存在')
        abort(404)
    if not current_user.is_following(user):
        flash('您并未关注该用户')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    flash('已取消关注%s' % user.username)
    return redirect(url_for('main.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('该用户不存在')
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.order_by(Follow.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    follows = [{'user':item.follower, 'timestamp':item.timestamp } for item in pagination.items]
    return render_template('follows.html', pagination=pagination, follows=follows,
                           user=user, endpoint='main.followers', title='的关注者')


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('该用户不存在')
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.order_by(Follow.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('follows.html', pagination=pagination, follows=follows,
                           user=user, endpoint='main.followed_by', title='关注的人')


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


@main.route('/moderate')
@permission_required(Permission.MODERATE_COMMENTS)  # 通过在moderate.html设置{% set moderate = True %}使得只有该页面能进入禁封
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)  # 当前页pagination.page
    comments = pagination.items
    return render_template('moderate.html', comments=comments, pagination=pagination, page=page)  # 为向评论able提供当前页面信息


@main.route('/moderate/enable/<int:id>')
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    if comment.disabled:
        comment.disabled = False
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('main.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    if not comment.disabled:
        comment.disabled = True
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('main.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/admin')
@admin_required
def for_admins_only():
    return "For administrators!"


@main.route('/moderator')
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"