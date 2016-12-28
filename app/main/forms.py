from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class NameForm(FlaskForm):
    name = StringField('What\'s your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name = StringField('名称:', validators=[Length(0,32)])
    location = StringField('所在地：', validators=[Length(0,64)])
    about_me = TextAreaField('关于我：')
    submit = SubmitField('更新提交')