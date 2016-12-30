from . import main
from flask import render_template


@main.app_errorhandler(403)
def page_not_found(e):  # 这个e是不是可以省略
    return render_template('403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):  # 这个e是不是可以省略
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):  # 这个e是不是可以省略
    return render_template('500.html'), 500
