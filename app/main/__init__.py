from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors  # 这里还要再导入模块，把路由和错误处理与main蓝图关联
from ..models import Permission


@main.app_context_processor  # main.app_context_processor(lambda :dict(Permission=Permission))
def inject_permissions():
    return dict(Permission=Permission)
