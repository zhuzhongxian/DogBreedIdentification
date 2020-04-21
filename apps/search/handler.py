import json
import os

from playhouse.shortcuts import model_to_dict
import matplotlib.pyplot as plt
import cv2
import collections
import math
from collections import namedtuple
import mxnet as mx
import numpy as np
from mxnet import autograd, gluon, init, nd
from mxnet.gluon import data as gdata, loss as gloss, model_zoo, nn
from mxnet.gluon.model_zoo import vision as models

from DogBreedIdentification.handler import RedisHandler
from apps.search.forms import BreedCommentForm,CommentReplyForm,SearchTextForm
from apps.utils.re_decorators import authenticated_async
from apps.search.models import DogBreed,BreedComment,CommentLike,DogFollower
from apps.users.models import User
from apps.message.models import Message
from apps.utils.util_func import json_serial

from keras.models import Model, load_model, save_model
from keras.layers import Input, Conv2D, MaxPooling2D, Dropout, BatchNormalization, Dense, GlobalAveragePooling2D
import numpy as np
from keras.utils.np_utils import to_categorical
import matplotlib.pyplot as plt
import cv2
from glob import glob
import random

class SearchHandler(RedisHandler):

    @authenticated_async
    async def post(self, *args, **wkargs):
        re_data = {}

        style=self.get_argument("style", None)
        # post image
        if(style=="image"):



            files_meta = self.request.files.get("image", None)
            if not files_meta:
                self.set_status(400)
                re_data["image"] = "请上传图片"
            else:
                # save image and set log
                # write file by aiofiles
                new_filename = ""
                for meta in files_meta:
                    #print(meta['body'])
                    img = meta['body']
                    img = np.frombuffer(img, np.uint8)  # 转成8位无符号整型
                    img = cv2.imdecode(img, cv2.IMREAD_COLOR)  #



                    # image perprocessing

                    # width = 299
                    # height = 299
                    # new_img = cv2.resize(img, (width, height))
                    # g = new_img[:, :, 1]
                    # b = new_img[:, :, 0]
                    # r = new_img[:, :, 2]
                    #
                    #
                    # image = cv2.merge((r, g, b))
                    #
                    # plt.imshow(image)
                    # plt.axis('off')
                    # plt.show()
                    # print(img.shape)
                    # X_299_test = nd.zeros((1, 3, 299, 299))
                    # X_299_test = mx.nd.array(image)
                    # transformer = gdata.vision.transforms.ToTensor()
                    # print(transformer(X_299_test))
                    # data_test_iter_299 = gluon.data.DataLoader(gluon.data.ArrayDataset(transformer(X_299_test)),
                    #                                            batch_size=128, last_batch='keep')
                    # x = []
                    # features = []
                    # net1 = models.get_model('inceptionv3', pretrained=True)
                    # for data_iter in data_test_iter_299:
                    #     data_iter = data_iter.reshape(1, 3, 299, 299)
                    #     print(data_iter)
                    #     feature = net1.features(data_iter)
                    #     print(feature)
                    #     feature = gluon.nn.Flatten()(feature)
                    #     features.append(feature.as_in_context(mx.cpu()))
                    # x = nd.concat(*features, dim=0)
                    # print(x)
                    # symnet = mx.symbol.load('test-symbol.json')
                    # mod = mx.mod.Module(symbol=symnet, context=mx.cpu())
                    # mod.bind(data_shapes=[('data', (1, 2048))])
                    # mod.load_params('test-0000.params')
                    # Batch = namedtuple('Batch', ['data'])
                    # mod.forward(Batch([x]))
                    # out = mod.get_outputs()
                    # prob = out[0]
                    # print(prob)
                    #predicted_labels = prob.argmax(axis=1)
                    #ident = predicted_labels.asnumpy()

                    ######### keras
                    model = load_model('D:/PycharmProjects/Dog_Breed_Identification/apps/search/model1.h5')
                    img = cv2.resize(img, (200, 200))
                    model_input = cv2.cvtColor(img.astype(np.float32), cv2.COLOR_BGR2RGB)

                    pred = model.predict(np.reshape(model_input, [1, 200, 200, 3]))
                    predicted_labels = pred.argmax(axis=1)
                    print(predicted_labels[0])
                    #ident = predicted_labels.asnumpy()
                    #print(ident+1)
                    # get infor from database
                    breed = await self.application.objects.get(DogBreed, DogIdentifier = int(predicted_labels[0]+1))
                    breed.SearchNum += 1
                    await self.application.objects.update(breed)
                    re_data["identifier"] = breed.DogIdentifier
                    re_data["name"] = breed.DogName

        # post text
        else:
            param = self.request.body.decode("utf-8")
            param = json.loads(param)
            form = SearchTextForm.from_json(param)

            if form.validate():
                print(form.name.data)

                dogbreed = await self.application.objects.execute(DogBreed.select().where(DogBreed.DogAlias.contains(str(form.name.data))))
                for item in dogbreed:
                    item.SearchNum += 1
                    await self.application.objects.update(item)
                    re_data["identifier"] = item.DogIdentifier


        self.finish(re_data)

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
        self.finish(json.dumps(re_data, default=json_serial))

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

        comment_replys = await self.application.objects.execute(
            BreedComment.select(BreedComment, User.id, User.NickName, User.HeadUrl).join(User, on=User.id == BreedComment.User_id).where(
                BreedComment.ParentComment_id == int(comment_id)).order_by(BreedComment.id.asc()))

        for item in comment_replys:
            reply_user = await self.application.objects.get(User,id=item.ReplyUser_id)
            item_dict = {
                #"user":model_to_dict(item.User),
                "author":{
                  "id":  item.User.id,
                  "nick_name":item.User.NickName,
                  "head_url":"{}/media/{}".format(self.settings["SITE_URL"], item.User.HeadUrl)
                },
                "relyed_user":{
                  "id":  reply_user.id,
                  "nick_name":reply_user.NickName
                },
                "content":item.Content,
                "reply_num":item.ReplyNum,
                "add_time":item.add_time.strftime("%Y-%m-%d"),
                "id":item.id
            }
            re_data.append(item_dict)

        self.finish(json.dumps(re_data,default=json_serial))

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
                                                              ReplyUser=replyed_user.id, Content=form.content.data)

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
    # user get follow info
    @authenticated_async
    async def get(self, breed_id, *args, **kwargs):
        try:
            re_data = {}
            follow = await self.application.objects.get(DogFollower, User_id=self.current_user.id, Breed_id=breed_id)
            re_data["follow"] = "true"


        except DogFollower.Exception:
            self.set_status(500)

        self.finish(re_data)
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

class BreedCancelFollowHandler(RedisHandler):
        # user cancel follow breed
        @authenticated_async
        async def post(self, breed_id, *args, **kwargs):
            try:
                re_data = {}
                u_id =self.current_user.id
                breed = await self.application.objects.get(DogBreed, id=int(breed_id))
                follow = await self.application.objects.execute(DogFollower.delete().where((DogFollower.User_id == u_id) & ( DogFollower.Breed_id == breed.id)))
                #re_data["id"] = follow.id
                re_data = "success"
                # update number
                breed.FollowerNum -= 1
                await self.application.objects.update(breed)

            except DogBreed.DoesNotExist as e:
                self.set_status(404)
            except DogFollower.Exception:
                self.set_status(500)

            self.finish(re_data)

class BreedLikeHandler(RedisHandler):
    # user adds like/dislike
    @authenticated_async
    async def post(self, breed_id, *args, **kwargs):
        try:
            re_data = {}
            breed = await self.application.objects.get(DogBreed, id=int(breed_id))
            # check in the set
            flag = self.redis_conn.sismember("breed_{}".format(breed_id),"user_{}".format(self.current_user.id))
            # user has liked
            if flag :
                # remove recode
                self.redis_conn.srem("breed_{}".format(breed_id),"user_{}".format(self.current_user.id))
                re_data['has_liked'] = 'false'
            # user has not liked
            else:
                # add record
                self.redis_conn.sadd("breed_{}".format(breed_id),"user_{}".format(self.current_user.id))
                re_data['has_liked'] = 'true'

        except DogBreed.DoesNotExist as e:
            self.set_status(404)


        self.finish(re_data)

    # get like/dislike number
    @authenticated_async
    async def get(self, breed_id, *args, **kwargs):
        try:
            re_data = {}
            breed = await self.application.objects.get(DogBreed, id=int(breed_id))
            re_data['has_liked'] = self.redis_conn.sismember("breed_{}".format(breed_id), "user_{}".format(self.current_user.id))
            re_data['like_num'] = self.redis_conn.scard("breed_{}".format(breed_id))

        except DogBreed.DoesNotExist as e:
            self.set_status(404)

        self.finish(re_data)

