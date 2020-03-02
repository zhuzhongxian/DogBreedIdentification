from wtforms_tornado import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class PostForm(Form):
    content = StringField("内容",validators=[DataRequired("请输入内容")])