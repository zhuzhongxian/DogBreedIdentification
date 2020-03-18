from peewee import *

from DogBreedIdentification.models import BaseModel


class Admin(BaseModel):
    Username = CharField(max_length=320, verbose_name="用户名", unique=True, index=True, default='admin')
    Password = CharField(verbose_name='密码', max_length=20, null=False, default='admin')

OPERATION_TYPE = (
    (1,"修改账号"),
    (2,"删除账号"),
    (3,"修改详情"),
    (4,"删除评论"),
)

class AdminLog(BaseModel):
    Admin = ForeignKeyField(Admin,verbose_name="管理员")
    OperationType = IntegerField(choices=OPERATION_TYPE,verbose_name="操作类型")