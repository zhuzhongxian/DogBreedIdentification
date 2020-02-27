from datetime import datetime

from DogBreedIdentification.settings import database
from peewee import *

class BaseModel(Model):
    add_time = DateTimeField(default=datetime.now(),verbose_name="插入时间")
    class Meta:
        database = database