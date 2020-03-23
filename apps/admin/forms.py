from wtforms_tornado import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class AdminLoginForm(Form):
    username = StringField("用户名",
                        validators=[DataRequired(message="请输入用户名")])
    password = StringField("密码", validators=[DataRequired(message="请输入密码")])

class ChangePasswordForm(Form):
    new_password = StringField("新密码", validators=[DataRequired("请输入新密码")])
    confirm_password = StringField("确认密码", validators=[DataRequired("请输入确认密码")])

class ChangeBreedForm(Form):
    dog_identifier = StringField("品种标识符")
    dog_name = StringField("品种名称")
    dog_alias = StringField("别名")
    dog_eng_name = StringField("英文名")
    dog_origin = StringField("产地")
    dog_weight = StringField("体重")
    dog_hight = StringField("身高")
    dog_life_span = StringField("寿命")
    dog_price = StringField("价格")
    dog_desc = StringField("品种简介")