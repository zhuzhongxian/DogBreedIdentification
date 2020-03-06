from wtforms_tornado import Form
from wtforms import StringField
from wtforms.validators import DataRequired, length

class BreedCommentForm(Form):
    context = StringField("内容",validators=[DataRequired("请输入评论的内容"),
                                           length(min=3, message="内容不能少于3个字")])