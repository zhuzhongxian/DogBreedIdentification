import json
import os

import aiofiles

from DogBreedIdentification.handler import AdminRedisHandler
from apps.admin.forms import AdminLoginForm,ChangePasswordForm,ChangeBreedForm
from apps.users.models import User
from apps.search.models import DogBreed,BreedComment
from apps.admin.models import AdminLog,Admin
from apps.utils.util_func import json_serial


class AdminLoginHandler(AdminRedisHandler):
    # admin login
    async def post(self, *args, **kwargs):
        re_data = {}
        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        form = AdminLoginForm.from_json(param)
        if form.validate():
            username = form.username.data
            password = form.password.data
            try:
                admin = await self.application.objects.get(Admin,UserName=username)
                if password != admin.Password:
                    re_data["non_fields"] = "账号或密码错误"
                else:
                    re_data["id"]=admin.id
                    re_data["username"]=username
                    self.redis_conn.set("{}_{}".format(admin.id, username), 1, 7 * 24 * 3600)
                    re_data["token"]="{}_{}".format(admin.id, username)
            except Admin.DoesNotExist as e:
                self.set_status(404)
                re_data["username"] = "管理员不存在"

        self.finish(re_data)

class AdminAccountsHandler(AdminRedisHandler):
    # get all accounts
    async def get(self, *args, **kwargs):
        re_data = []
        token = self.request.headers.get("sessionid", None)
        if not self.redis_conn.get(token):
            self.set_status(400)
        else:
            users = await self.application.objects.execute(User.select())
            for user in users:
                re_data.append({
                    "id":user.id,
                    "email":user.Email,
                    "nick_name":user.NickName
                })

        self.finish(json.dumps(re_data))

class ManageAccountsHandler(AdminRedisHandler):
    # change password
    async def post(self, user_id, *args, **kwargs):
        re_data = {}
        token = self.request.headers.get("sessionid", None)
        if not self.redis_conn.get(token):
            re_data["notlogin"]="true"
            self.set_status(400)
        else:
            param = self.request.body.decode("utf-8")
            param = json.loads(param)
            form = ChangePasswordForm.from_json(param)
            if form.validate():
                if form.new_password.data != form.confirm_password.data:
                    re_data["new_password"] = "两次密码不一致"
                else:
                    try:
                        admin_id = token.split("_")
                        user = await self.application.objects.get(User, id=user_id)
                        user.Password = form.new_password.data
                        await self.application.objects.update(user)
                        await self.application.objects.create(AdminLog, Admin=admin_id[0], OperationType=1)
                    except User.DoesNotExist as e:
                        self.set_status(404)
                        re_data["id"] = "用户不存在"

        self.finish(re_data)

    # delete account
    async def delete(self, user_id, *args, **kwargs):
        re_data = {}
        token = self.request.headers.get("sessionid", None)
        if not self.redis_conn.get(token):
            self.set_status(400)
        else:
            try:
                admin_id=token.split("_")
                user = await self.application.objects.get(User, id=int(user_id))
                await self.application.objects.execute(User.delete().where(User.id == user.id))
                # add log
                await self.application.objects.create(AdminLog, Admin=admin_id[0], OperationType=2)
            except User.DoesNotExist as e:
                self.set_status(404)

        self.finish(re_data)

class AdminBreedsHandler(AdminRedisHandler):
    # get all breeds
    async def get(self, *args, **kwargs):
        re_data = []
        token = self.request.headers.get("sessionid", None)
        if not self.redis_conn.get(token):
            self.set_status(400)
        else:
            breeds = await self.application.objects.execute(DogBreed.select())
            for breed in breeds:
                re_data.append({
                    "id":breed.id,
                    "dog_name":breed.DogName,
                    "dog_origin":breed.DogOrigin,
                    "dog_image":"{}/media/{}".format(self.settings["SITE_URL"],breed.DogImage),
                    "dog_search_num": breed.SearchNum,
                    "dog_follower_num": breed.FollowerNum,
                    "dog_comment_num": breed.CommentNum
                })
        self.finish(json.dumps(re_data))

    # add a breed
    async def post(self, *args, **kwargs):
        re_data = {}
        token = self.request.headers.get("sessionid", None)
        if not self.redis_conn.get(token):
            self.set_status(400)
        else:
            admin_id = token.split("_")
            param = self.request.body.decode("utf-8")
            param = json.loads(param)
            form = ChangeBreedForm.from_json(param)
            if form.validate():
                iden = int(form.dog_identifier.data)

                await self.application.objects.create(DogBreed, DogIdentifier = iden,
                DogName = form.dog_name.data,
                DogAlias = form.dog_alias.data,
                DogEngName = form.dog_eng_name.data,
                DogOrigin = form.dog_origin.data,
                DogWeight = form.dog_weight.data,
                DogHight = form.dog_hight.data,
                DogLifeSpan = form.dog_life_span.data,
                DogPrice = form.dog_price.data,
                DogImage = "define.png",
                DogDesc = form.dog_desc.data,)
                await self.application.objects.create(AdminLog, Admin=admin_id[0], OperationType=6)

            else:
                self.set_status(400)
                for field in form.errors:
                    re_data[field] = form.errors[field][0]

        self.finish(json.dumps(re_data))

class ManageBreedsHandler(AdminRedisHandler):
    # get breed text info
    async def get(self, breed_id, *args, **kwargs):

        try:
            breed = await self.application.objects.get(DogBreed, DogIdentifier=breed_id)
            re_data = {
                "dog_id": breed.id,
                "dog_identifier": breed.DogIdentifier,
                "dog_name": breed.DogName,
                "dog_alias": breed.DogAlias,
                "dog_eng_name": breed.DogEngName,
                "dog_origin": breed.DogOrigin,
                "dog_weight": breed.DogWeight,
                "dog_hight": breed.DogHight,
                "dog_life_span": breed.DogLifeSpan,
                "dog_price": breed.DogPrice,
                #"dog_image": "/media/" + breed.DogImage,
                "dog_desc": breed.DogDesc
            }
        except DogBreed.DoesNotExist as e:
            self.set_status(404)

        self.finish(re_data)

    # change breeds text info
    async def patch(self, breed_id, *args, **kwargs):
        re_data = {}
        token = self.request.headers.get("sessionid", None)
        if not self.redis_conn.get(token):
            re_data["notlogin"] = "true"
            self.set_status(400)
        else:
            admin_id = token.split("_")
            param = self.request.body.decode("utf-8")
            param = json.loads(param)
            form = ChangeBreedForm.from_json(param)
            if form.validate():
                try:

                    breed = await self.application.objects.get(DogBreed, DogIdentifier=breed_id)
                    await self.application.objects.create(AdminLog, Admin=admin_id[0], OperationType=3)
                    iden = int(form.dog_identifier.data)
                    breed.DogIdentifier = iden
                    breed.DogName = form.dog_name.data
                    breed.DogAlias = form.dog_alias.data
                    breed.DogEngName = form.dog_eng_name.data
                    breed.DogOrigin = form.dog_origin.data
                    breed.DogWeight = form.dog_weight.data
                    breed.DogHight = form.dog_hight.data
                    breed.DogLifeSpan = form.dog_life_span.data
                    breed.DogPrice = form.dog_price.data
                    breed.DogDesc = form.dog_desc.data
                    await self.application.objects.update(breed)
                except DogBreed.DoesNotExist as e:
                    self.set_status(404)
            else:
                self.set_status(400)
                for field in form.errors:
                    re_data[field] = form.errors[field][0]
        self.finish(re_data)

    # delete breeds info
    async def delete(self, breed_id, *args, **kwargs):
        re_data = {}
        token = self.request.headers.get("sessionid", None)
        if not self.redis_conn.get(token):
            re_data["notlogin"] = "true"
            self.set_status(400)
        else:
            admin_id = token.split("_")

            await self.application.objects.create(AdminLog, Admin=admin_id[0], OperationType=5)
            await self.application.objects.execute(DogBreed.delete().where(DogBreed.id == breed_id))
            re_data["del"] = "success"

        self.finish(re_data)

class ManageImageHandler(AdminRedisHandler):
    # get image
    async def get(self, breed_id, *args, **kwargs):
        try:
            breed = await self.application.objects.get(DogBreed, DogIdentifier=breed_id)
        except DogBreed.DoesNotExist as e:
            self.set_status(404)

        self.finish({
            "image":"/media/" + breed.DogImage
        })
    # change image data
    async def post(self, breed_id,*args, **kwargs):
        re_data = {}
        token = self.request.headers.get("sessionid", None)
        if not self.redis_conn.get(token):
            self.set_status(400)
        else:
            files_meta = self.request.files.get("image", None)
            if not files_meta:
                self.set_status(400)
                re_data["image"]="请上传图片"
            else:
                # save image and set log
                # write file by aiofiles
                admin_id = token.split("_")
                new_filename = ""
                breed = await self.application.objects.get(DogBreed,DogIdentifier=breed_id)
                for meta in files_meta:
                    filename = meta["filename"]
                    end = filename.split(".")
                    new_filename = "{filename}.{end}".format(filename=breed.DogIdentifier,end=end[1])
                    file_path = os.path.join(self.settings["MEDIA_ROOT"], new_filename)
                    async with aiofiles.open(file_path,'wb') as f:
                        await f.write(meta['body'])
                        re_data["image"] = "/media/" + new_filename

                    breed.DogImage = new_filename
                    await self.application.objects.update(breed)
                    await self.application.objects.create(AdminLog, Admin=admin_id[0], OperationType=3)

        self.finish(re_data)

class AdminCommentsHandler(AdminRedisHandler):
    # get all comments
    async def get(self, *args, **kwargs):
        re_data = []
        token = self.request.headers.get("sessionid", None)
        if not self.redis_conn.get(token):
            re_data["notlogin"]="true"
            self.set_status(400)
        else:
            comments = await self.application.objects.execute(BreedComment.select().where(BreedComment.ParentComment.is_null(True)).order_by(BreedComment.add_time.desc()))
            for comment in comments:

                user = await self.application.objects.get(User,id=comment.User_id)
                breed = await self.application.objects.get(DogBreed,id=comment.Breed_id)
                re_data.append({
                    "id":comment.id,
                    "nick_name": user.NickName,
                    "dog_name": breed.DogName,
                    "content":comment.Content,
                    "add_time":comment.add_time
                })
        self.finish(json.dumps(re_data, default=json_serial))

class ManageCommentsHandler(AdminRedisHandler):
    # manage comments
    async def delete(self, comment_id, *args, **kwargs):
        re_data = {}
        token = self.request.headers.get("sessionid", None)
        if not self.redis_conn.get(token):
            re_data["notlogin"] = "true"
            self.set_status(400)
        else:
            try:
                admin_id = token.split("_")
                comment = await self.application.objects.get(BreedComment,id=int(comment_id))
                await self.application.objects.execute(BreedComment.delete().where(BreedComment.id==comment.id))
                # add log
                await self.application.objects.create(AdminLog, Admin=admin_id[0], OperationType=4)
            except BreedComment.DoesNotExist as e:
                self.set_status(404)

        self.finish(re_data)

class LogsHandler(AdminRedisHandler):
    # show log
    async def get(self, *args, **kwargs):
        re_data = []
        token = self.request.headers.get("sessionid", None)
        if not self.redis_conn.get(token):
            self.set_status(400)
        else:
            logs = await self.application.objects.execute(AdminLog.select().order_by(AdminLog.add_time.asc()))
            for log in logs:
                re_data.append({
                    "id":log.id,
                    "admin_id":log.Admin_id,
                    "add_time":log.add_time,
                    "operation_type":log.OperationType
                })

        self.finish(json.dumps(re_data, default=json_serial))
