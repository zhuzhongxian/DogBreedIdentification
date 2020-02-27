from wtforms_tornado import Form
from wtforms import StringField
from wtforms.validators import DataRequired,Regexp

Email_REGEX = "^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$"

class EmailCodeForm(Form):
    email = StringField("邮箱地址",
                        validators=[DataRequired(message="请输入邮箱"), Regexp(Email_REGEX)])
class RegisterForm(Form):
    email = StringField("邮箱地址",
                        validators=[DataRequired(message="请输入邮箱"), Regexp(Email_REGEX)])
    code = StringField("验证码", validators=[DataRequired(message="请输入验证码")])
    password = StringField("密码",validators=[DataRequired(message="请输入密码")])
class LoginForm(Form):
    email = StringField("邮箱地址",
                        validators=[DataRequired(message="请输入邮箱"), Regexp(Email_REGEX)])
    password = StringField("密码", validators=[DataRequired(message="请输入密码")])