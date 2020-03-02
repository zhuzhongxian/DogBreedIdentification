from peewee import *
from datetime import datetime

from DogBreedIdentification.models import BaseModel
from apps.users.models import User

class DogBreed(BaseModel):
    DogIdentifier = IntegerField(verbose_name="标识符")
    DogName = CharField(max_length=100, null=True, verbose_name="名称")
    DogAlias = CharField(max_length=100, null=True, verbose_name="别名")
    DogEngName = CharField(max_length=100, null=True, verbose_name="外文名称")
    DogOrigin = CharField(max_length=50, null=True, verbose_name="产地")
    DogWeight = CharField(max_length=20, null=True, verbose_name="平均体重")
    DogHight = CharField(max_length=20, null=True, verbose_name="平均身高")
    DogLifeSpan = CharField(max_length=20, null=True, verbose_name="平均寿命")
    DogPrice = CharField(max_length=20, null=True, verbose_name="市场价格")
    DogImage = CharField(max_length=200, null=True, verbose_name="狗的图片")
    DogDesc = TextField(verbose_name="狗的简介")

    SearchNum = IntegerField(default=0, verbose_name="搜索数")
    FollowerNum = IntegerField(default=0, verbose_name="关注")
    PostNum = IntegerField(default=0, verbose_name="帖子数")

class DogFollower(BaseModel): #uncompleted
    User = ForeignKeyField(User,verbose_name="用户")
    Breed = ForeignKeyField(DogBreed,verbose_name="狗的品种")

class Post(BaseModel):
    User = ForeignKeyField(User, verbose_name="用户")
    Breed = ForeignKeyField(DogBreed, verbose_name="种类")
    CommentNum = IntegerField(default=0, verbose_name="评论数")
    Content = TextField(verbose_name="内容")

class PostComment(BaseModel):
    User = ForeignKeyField(User,verbose_name="用户",related_name="author")
    Post = ForeignKeyField(Post,verbose_name="帖子")
    ParentComment = ForeignKeyField('self',null=True,verbose_name="评论",related_name="comments_parent")
    ReplyUser = ForeignKeyField(User,verbose_name="用户",related_name="replyed_author",null=True)
    Context = CharField(max_length=1000,verbose_name="内容")
    ReplyNum = IntegerField(default=0,verbose_name="回复数")
    LikeNum = IntegerField(default=0,verbose_name="点赞数")

class CommentLike(BaseModel):
    User = ForeignKeyField(User,verbose_name="用户")
    PostComment = ForeignKeyField(PostComment,verbose_name="帖子")

