from peewee import *
from apps.users.models import User
#db = MySQLDatabase("dogbreedidentification", host="localhost", port=3306, user="root", password="123456")
from datetime import datetime

import jwt

current_time = datetime.utcnow()

data = jwt.encode({
    "name" : "zzx",
    "id" : 1,
    "exp" : current_time
}, "aaa")
data1 = data.decode("utf-8")

print(data,data1)
import time
time.sleep(2)
mm = jwt.decode(data,"aaa",leeway = 3,options={"verify_exp" : True})
print(mm)


#if __name__ == "__main__":
    # 执行test1这个类，进行创建数据表
    #db.create_tables([User])
