from . import api
from flask import request, g, jsonify, current_app, url_for
from .errors import ValidationError
from ..models import Comment, Post, Permission
from .. import db
from .decorators import permission_required


@api.route('/posts/<int:id>/comments')
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return jsonify({
        'posts': [comment.to_json() for comment in comments],
        'prev': url_for('api.get_post_comments', id=post.id, page=page - 1, _external=True) if pagination.has_prev else None,
        'next': url_for('api.get_post_comments', id=post.id, page=page + 1, _external=True) if pagination.has_next else None,
        'count': pagination.total  # 总数
    })


@api.route('/posts/<int:id>/comments', methods=['POST'])
@permission_required(Permission.COMMENT)
def new_post_comment(id):
    post = Post.query.get_or_404(id)
    content = request.json.get('content')
    if not content:
        raise ValidationError('Comment with no content')
    comment = Comment(content=content, auth=g.current_user, post=post)
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, {'Location':url_for('api.get_comment', id=comment.id, _external=True)}

@api.route('/comments/')
def get_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return jsonify({
        'posts': [comment.to_json() for comment in comments],
        'prev': url_for('api.get_comments', page=page - 1, _external=True) if pagination.has_prev else None,
        'next': url_for('api.get_comments', page=page + 1, _external=True) if pagination.has_next else None,
        'count': pagination.total  # 总数
    })

@api.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())