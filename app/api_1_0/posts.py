from . import api
from flask import request, g, jsonify, url_for, current_app
from .errors import ValidationError, forbidden
from ..models import Post, Permission
from .. import db
from .decorators import permission_required


@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return jsonify({
        'posts':[post.to_json() for post in posts],
        'prev':url_for('api.get_posts', page=page-1, _external=True) if pagination.has_prev else None,
        'next':url_for('api.get_posts', page=page+1, _external=True) if pagination.has_next else None,
        'count':pagination.total  # 总数
    })


@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    content = request.json.get('content')
    if not content:
        raise ValidationError('Post with no content')
    post = Post(content=content, auth=g.current_user)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, {'Location':url_for('api.get_post', id=post.id, _external=True)}  # 增加重定向响应报头Location


@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.auth and not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    post.content = request.json.get('content', post.content)  # 省
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())
