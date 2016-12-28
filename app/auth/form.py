from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('电子邮箱:', validators=[DataRequired(), Length(1, 64), Email('邮件地址无效')])
    password = PasswordField('密码:', validators=[DataRequired(), Length(6, 32, '长度介于6-32')])
    remember_me = BooleanField('自动登录')  # 是否cookie
    submit = SubmitField('确认')


class RegisterForm(FlaskForm):
    email = StringField('电子邮箱:', validators=[DataRequired(), Length(1, 64), Email('邮件地址无效')])
    username = StringField('用户名:', validators=[DataRequired(), Length(2, 32, '长度介于2-32'),
                                               Regexp('^[a-zA-Z][a-zA-Z0-9\_\.]*$', message='用户名以字母开头，可包含数字下划线与.')])
    password = PasswordField('密码:', validators=[DataRequired(), Length(6, 32, '长度介于6-32'),
                                                EqualTo('password2', message='两次密码不同')])  # EqualTo的1参为fieldname字符串
    password2 = PasswordField('确认密码:', validators=[DataRequired()])
    submit = SubmitField('确认注册')

    def validate_email(self, email):  # 要传递的是属性，要返回的是Error
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('该邮箱已被注册！')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('该用户名已被注册！')