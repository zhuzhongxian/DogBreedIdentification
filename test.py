from peewee import *
from apps.users.models import User
db = MySQLDatabase("dogbreedidentification", host="localhost", port=3306, user="root", password="123456")




if __name__ == "__main__":
    # 执行test1这个类，进行创建数据表
    db.create_tables([User])
