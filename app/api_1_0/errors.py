from . import api
from flask import jsonify
# json 错误返回通常对象属性为：error，data, message


class ValidationError(ValueError):
    pass


def bad_request(message):
    response = jsonify({'error':'bad request','message':message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error':'unauthorized','message':message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error':'forbidden','message':message})
    response.status_code = 403
    return response


@api.errorhandler(ValidationError)  # 验证POST提交内容
def validation_error(e):
    return bad_request(e.args[0])