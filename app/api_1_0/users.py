from . import api
from ..models import User, Post
from flask import jsonify, request, current_app, url_for


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api.route('/users/<int:id>/posts')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return jsonify({
        'posts':[post.to_json() for post in posts],
        'prev':url_for('api.get_user_posts', id=user.id, page=page-1, _external=True) if pagination.has_prev else None,
        'next':url_for('api.get_user_posts', id=user.id, page=page+1, _external=True) if pagination.has_next else None,
        'count':pagination.total  # 总数
    })


@api.route('/users/<int:id>/timeline/')  # 该user的following的posts
def get_user_followed_posts(id):  # 未必是g.current_user的
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return jsonify({
        'posts':[post.to_json() for post in posts],
        'prev':url_for('api.get_user_followed_posts', id=user.id,
                       page=page - 1, _external=True) if pagination.has_prev else None,
        'next':url_for('api.get_user_followed_posts', id=user.id,
                       page=page + 1, _external=True) if pagination.has_next else None,
        'count':pagination.total
    })