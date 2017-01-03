# 基于flask_httpauth的用户认证
from functools import wraps
from flask import g
from .errors import forbidden


def permission_required(permission):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('Insufficient permission')  # 修改main.errors 中的403兼容abort(403)也可
            return fn(*args, **kwargs)
        return wrapper
    return decorator
