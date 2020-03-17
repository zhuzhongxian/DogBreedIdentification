from wtforms_tornado import Form
from wtforms import StringField
from wtforms.validators import DataRequired,Regexp,AnyOf

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
class ProfileForm(Form):
    nick_name = StringField("昵称", validators=[DataRequired("请输入昵称")])
    gender = StringField("性别", validators=[AnyOf(values=["female","male"])])
    desc = StringField("个人简介")
class ChangePasswordForm(Form):
    old_password = StringField("旧密码", validators=[DataRequired("请输入旧密码")])
    new_password = StringField("新密码", validators=[DataRequired("请输入新密码")])
    confirm_password = StringField("确认密码", validators=[DataRequired("请输入确认密码")])