import json

from playhouse.shortcuts import model_to_dict

from DogBreedIdentification.handler import RedisHandler
from apps.search.forms import BreedCommentForm,CommentReplyForm
from apps.utils.re_decorators import authenticated_async
from apps.search.models import DogBreed,BreedComment,CommentLike,DogFollower
from apps.users.models import User
from apps.message.models import Message
from apps.utils.util_func import json_serial


class BreedHandler(RedisHandler):

    async def get(self, *args, **wkargs):
        re_data = []
        dog_breed_query = DogBreed.select()

        order = self.get_argument("o", None)
        if order:
            if order == "hot": # get hot breed
                dog_breed_query = dog_breed_query.order_by(DogBreed.SearchNum.desc())

        limit = self.get_argument("limit", None)
        if limit:
            dog_breed_query = dog_breed_query.limit(int(limit))

        breeds = await self.application.objects.execute(dog_breed_query)
        for breed in breeds:
            breed_dict = model_to_dict(breed)
            breed_dict["DogImage"] = "{}/media/{}".format(self.settings["SITE_URL"],breed_dict["DogImage"])
            re_data.append(breed_dict)

        self.finish(json.dumps(re_data,default=json_serial))

        #token = self.request.headers.get("token",None)

class BreedDetailHandler(RedisHandler):

    @authenticated_async
    async def get(self, breed_id, *args, **kwargs):
        # get breed detail
        re_data = {}
        try:
            breed = await self.application.objects.get(DogBreed, DogIdentifier = int(breed_id))
            breed_dict = model_to_dict(breed)
            breed_dict["DogImage"] = "{}/media/{}".format(self.settings["SITE_URL"],breed_dict["DogImage"])
            re_data = breed_dict

        except DogBreed.DoseNotExist as e:
            self.set_status(404)

        self.finish(json.dumps(re_data,default=json_serial))

class BreedCommentHandler(RedisHandler):

    @authenticated_async
    async def get(self, breed_id, *args, **kwargs):
        # get comments
        re_data = []
        try:
            breed = await self.application.objects.get(DogBreed, DogIdentifier = int(breed_id))
            breed_comments = await self.application.objects.execute(BreedComment.select(BreedComment, User.id,User.NickName,User.HeadUrl).join(User, on=(User.id == BreedComment.User_id)).where(BreedComment.Breed_id == breed,BreedComment.ParentComment.is_null(True)).order_by(BreedComment.add_time.desc()))

            for item in breed_comments:
                print(item.User.NickName)
                item.User.HeadUrl = "{}/media/{}".format(self.settings["SITE_URL"], item.User.HeadUrl)
                has_liked = False
                try:
                    comments_like = await self.application.objects.get(CommentLike, BreedComment_id=item.id,
                                                                       User_id=self.current_user.id)
                    has_liked = True
                except CommentLike.DoesNotExist:
                    pass


                item_dict = {
                    "user" : model_to_dict(item.User),
                    "add_time": item.add_time,
                    "content" : item.Content,
                    "reply_nums" : item.ReplyNum,
                    "like_num" : item.LikeNum,
                    "has_liked" : has_liked,
                    "id" : item.id,
                }

                re_data.append(item_dict)
        except BreedComment.DoesNotExist as e:
            self.set_status(404)
        self.finish(self.finish(json.dumps(re_data, default=json_serial)))

    @authenticated_async
    async def post(self, breed_id, *args, **kwargs): #add comments
        re_data = {}
        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        form = BreedCommentForm.from_json(param)
        if form.validate():
            try:
                breed = await self.application.objects.get(DogBreed, DogIdentifier = breed_id)
                breed_comment = await self.application.objects.create(BreedComment, User = self.current_user,
                                                                      Breed = breed, Content = form.content.data)
                breed.CommentNum +=1
                await self.application.objects.update(breed)
                re_data["id"] = breed_id
                re_data["user"] = {}
                re_data["user"]["nick_name"] = self.current_user.NickName
                re_data["user"]["id"] = self.current_user.id
            except DogBreed.DoesNotExist as e:
                self.set_status(404)
        else:
            self.set_status(400)
            for field in form.errors:
                re_data[field] = form.errors[field][0]


        self.finish(re_data)

class CommentReplyHandler(RedisHandler):

    @authenticated_async
    async def get(self, comment_id, *args, **kwargs):
        re_data = []
        comment_replys = await self.application.objects.execute(BreedComment.select(BreedComment,User.id,User.NickName,User.HeadUrl).join(User,on=User.id==BreedComment.User_id).where(BreedComment.ParentComment_id==int(comment_id)))

        for item in comment_replys:
            item_dict = {
                #"user":model_to_dict(item.User),
                "user":{
                  "id":  item.User.id,
                  "nick_name":item.User.NickName,
                  "head_url":"{}/media/{}".format(self.settings["SITE_URL"], item.User.HeadUrl)
                },
                "content":item.Content,
                "reply_num":item.ReplyNum,
                "add_time":item.add_time.strftime("%Y-%m-%d"),
                "id":item.id
            }
            re_data.append(item_dict)

        self.finish(self.finish(json.dumps(re_data,default=json_serial)))

    @authenticated_async
    # add reply
    async def post(self, comment_id, *args, **kwargs):
        re_data = {}
        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        form = CommentReplyForm.from_json(param)
        if form.validate():
            try:
                comment = await self.application.objects.get(BreedComment, id=int(comment_id))
                replyed_user = await self.application.objects.get(User, id=form.replyed_user.data)
                reply = await self.application.objects.create(BreedComment, User=self.current_user, ParentComment=comment,
                                                              ReplyedUser=replyed_user, Content=form.content.data)

                # update reply number
                comment.ReplyNum +=1
                await self.application.objects.update(comment)
                re_data["id"] = reply.id
                re_data["user"] = {
                    "id":self.current_user.id,
                    "nickname": self.current_user.NickName
                }
                # send message
                await self.application.objects.create(Message, Sender=self.current_user, Receiver=replyed_user,
                                                      MessageType=1, ParentContent=comment.Content,
                                                      Message=form.content.data)
            except BreedComment.DoesNotExist as e:
                self.set_status(404)
            except User.DoesNotExist as e:
                self.set_status(400)
                re_data["replyed_user"] = "用户不存在"
        else:
            self.set_status(400)
            for field in form.errors:
                re_data[field] = form.errors[field][0]

        self.finish(re_data)

class CommentsLikeHandler(RedisHandler):

    @authenticated_async
    async def post(self,comment_id, *args, **kwargs):
        re_data = {}
        try:
            comment = await self.application.objects.get(BreedComment, id=int(comment_id))
            comment_like= await self.application.objects.create(CommentLike, User=self.current_user,BreedComment=comment)
            # update number
            comment.LikeNum += 1
            await self.application.objects.update(comment)

            re_data["id"] = comment_like.id

            # send message
            receiver = await self.application.objects.get(User, id=comment.User_id)
            await self.application.objects.create(Message, Sender=self.current_user, Receiver=receiver,
                                            MessageType=2, ParentContent=comment.Content,
                                            Message="")

        except BreedComment.DoesNotExist as e:
            self.set_status(404)

        self.finish(re_data)

class BreedFollowHandler(RedisHandler):
    # user follow breed
    @authenticated_async
    async def post(self, breed_id, *args, **kwargs):
        try:
            re_data = {}
            breed = await self.application.objects.get(DogBreed, id=int(breed_id))
            follow = await self.application.objects.create(DogFollower,User=self.current_user.id,Breed=breed)
            re_data["id"] = follow.id
            # update number
            breed.FollowerNum += 1
            await self.application.objects.update(breed)

        except DogBreed.DoesNotExist as e:
            self.set_status(404)
        except DogFollower.Exception:
            self.set_status(500)

        self.finish(re_data)


