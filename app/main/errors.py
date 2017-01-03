from . import main
from flask import render_template, request, jsonify  # flask.jsonify也是对import json包的包装


@main.app_errorhandler(403)
def page_forbidden(e):  # 这个e是不是可以省略
    return render_template('403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):  # 或代完成api的resouce_not_found
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:  # 可以通过request的dataType？
        response = jsonify({'error':'not found'})
        response.status_code = 404
        return response  # 返回json对象
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:  # 可以通过request的dataType？
        response = jsonify({'error':'internal server error'})
        response.status_code = 500
        return response
    return render_template('500.html'), 500
