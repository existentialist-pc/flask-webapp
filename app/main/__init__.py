from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors  # 这里还要再导入模块，把路由和错误处理与main蓝图关联
