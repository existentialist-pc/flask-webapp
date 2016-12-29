from ..models import User, Role
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp


class PostForm(FlaskForm):
    content = TextAreaField('写点什么？', validators=[DataRequired()])
    submit = SubmitField('确认')


class NameForm(FlaskForm):
    name = StringField('What\'s your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name = StringField('名称:', validators=[Length(0,32)])
    location = StringField('所在地：', validators=[Length(0,64)])
    about_me = TextAreaField('关于我：')
    submit = SubmitField('更新提交')


class EditProfileAdminForm(FlaskForm):
    email = StringField('电子邮箱:', validators=[DataRequired(), Length(1, 64), Email('邮件地址无效')])
    username = StringField('用户名:', validators=[
        DataRequired(),
        Length(2, 32, '长度介于2-32'),
        Regexp('^[a-zA-Z][a-zA-Z0-9\_\.]*$', message='用户名以字母开头，可包含数字下划线与.')
    ])
    confirmed = BooleanField('邮箱验证：')
    role = SelectField('用户类型', coerce=int)

    name = StringField('该用户名称:', validators=[Length(0,32)])
    location = StringField('该用户所在地：', validators=[Length(0,64)])
    about_me = TextAreaField('关于该用户：')
    submit = SubmitField('更新提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.id).all()]  # 传递元组，()
        self.user = user  # 用于验证未修改

    def validate_email(self, email):  # 要传递的是属性，验证不通过要引发Error
        if email != self.email and User.query.filter_by(email=email.data).first():
            raise ValidationError('该邮箱已被注册！')

    def validate_username(self, username):
        if username != self.username and User.query.filter_by(username=username.data).first():
            raise ValidationError('该用户名已被注册！')