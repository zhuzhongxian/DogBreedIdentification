from wtforms_tornado import Form
from wtforms import StringField,IntegerField
from wtforms.validators import DataRequired, length

class BreedCommentForm(Form):
    content = StringField("内容",validators=[DataRequired("请输入评论的内容"),
                                           length(min=3, message="内容不能少于3个字")])

class CommentReplyForm(Form):
    replyed_user = IntegerField("回复用户",validators=[DataRequired("请输入回复用户")])
    content = StringField("内容",validators=[DataRequired("请输入评论的内容"),
                                           length(min=3, message="内容不能少于3个字")])