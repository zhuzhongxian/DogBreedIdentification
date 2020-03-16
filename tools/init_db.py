from peewee import MySQLDatabase

from apps.users.models import User
from apps.search.models import DogBreed,DogFollower,BreedComment,CommentLike

from DogBreedIdentification.settings import database
database = MySQLDatabase("dogbreedidentification", host="127.0.0.1", port=3306, user="root", password="123456")



if __name__ == '__main__':
    #database.create_tables([User])
    #database.create_tables([DogFollower])
    database.create_tables([DogBreed])