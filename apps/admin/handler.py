import json

from DogBreedIdentification.handler import RedisHandler
from apps.users.models import User
from apps.search.models import DogBreed,BreedComment
from apps.admin.models import AdminLog


class AdminLoginHandler(RedisHandler):
    pass

class AdminAccountsHandler(RedisHandler):
    # get all accounts
    async def get(self, *args, **kwargs):
        re_data = []
        users = await self.application.objects.execute(User.select())
        for user in users:
            re_data.append({
                "id":user.id,
                "email":user.Email,
                "nick_name":user.NickName
            })

        self.finish(json.dumps(re_data))

class AdminBreedsHandler(RedisHandler):
    # get all breeds
    async def get(self, *args, **kwargs):
        re_data = []
        breeds = await self.application.objects.execute(DogBreed.select())
        for breed in breeds:
            re_data.append({
                "id":breed.id,
                "dog_name":breed.DogName,
                "dog_origin":breed.DogOrigin
            })
        self.finish(json.dumps(re_data))

class AdminCommentsHandler(RedisHandler):
    # get all comments
    async def get(self, *args, **kwargs):
        re_data = []
        comments = await self.application.objects.execute(BreedComment.select().where(BreedComment.ParentComment.is_null(True)))
        for comment in comments:
            user = await self.application.objects.get(User,id=comment.User_id)
            breed = await self.application.objects.get(DogBreed,id=comment.Breed_id)
            re_data.append({
                "id":comment.id,
                "nick_name": user.NickName,
                "dog_name": breed.DogName,
                "content":comment.Content
            })
        self.finish(json.dumps(re_data))

class ManageCommentsHandler(RedisHandler):
    # manage comments
    async def delete(self, comment_id, *args, **kwargs):
        re_data = {}
        try:
            comment = await self.application.objects.get(BreedComment,id=int(comment_id))
            await self.application.objects.execute(BreedComment.delete().where(BreedComment.id==comment.id))
            # add log
            await self.application.objects.create(AdminLog, Admin=1, OperationType=4)
        except BreedComment.DoesNotExist as e:
            self.set_status(404)

        self.finish(re_data)