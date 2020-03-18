from wtforms_tornado import Form
from wtforms import StringField,IntegerField
from wtforms.validators import DataRequired

class AdminLoginForm(Form):
    username = StringField("用户名",
                        validators=[DataRequired(message="请输入用户名")])
    password = StringField("密码", validators=[DataRequired(message="请输入密码")])