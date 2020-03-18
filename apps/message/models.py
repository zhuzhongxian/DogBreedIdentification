from peewee import *

from DogBreedIdentification.models import BaseModel
from apps.users.models import User

MESSAGE_TYPE = (
    (1,"回复"),
    (2,"点赞"),
)

class Message(BaseModel):
    Sender = ForeignKeyField(User,verbose_name="发送者")
    Receiver = ForeignKeyField(User,verbose_name="接收者")
    MessageType = IntegerField(choices=MESSAGE_TYPE,verbose_name="类别")
    Message = CharField(max_length=500,null=True,verbose_name="内容")
    ParentContent = CharField(max_length=500,null=True,verbose_name="操作的内容")