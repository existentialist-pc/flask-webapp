from functools import wraps
from flask import abort  # 自定义的错误返回
from flask_login import current_user
from .models import Permission


def permission_required(permission):  # 同@login_required实现
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

admin_required = permission_required(Permission.ADMINISTER)


#def admin_required(fn):
#    return permission_required(Permission.ADMINISTER)(fn)
