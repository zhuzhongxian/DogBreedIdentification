import json
from random import choice
from datetime import datetime
import uuid
import os

import jwt
import aiofiles

from apps.utils.re_decorators import authenticated_async
from apps.users.forms import EmailCodeForm,RegisterForm,LoginForm,ProfileForm,ChangePasswordForm
from apps.users.models import User
from DogBreedIdentification.handler import RedisHandler


class EmailCodeHandler(RedisHandler):
    def generate_code(self):
        seeds = "1234567890"
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))
        return "".join(random_str)
    async def post(self, *args, **kwargs):
        re_data = {}

        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        email_form = EmailCodeForm.from_json(param)
        if email_form.validate(): #send email with a code
            email = email_form.email.data
            #write code into redis
            code = self.generate_code()
            print(code,email)
            self.redis_conn.set("{}_{}".format(email, code), 1, 10 * 60)
        else:
            self.set_status(400)
            for field in email_form.errors:
                re_data[field] = email_form.errors[field][0]

        self.finish(re_data)

class RegisterHandler(RedisHandler):
    async def post(self, *args, **kwargs):
        re_data={}

        params = self.request.body.decode("utf-8")
        params = json.loads(params)
        register_form = RegisterForm.from_json(params)
        if register_form.validate():
            email = register_form.email.data
            code = register_form.code.data
            password = register_form.password.data
            redis_key = "{}_{}".format(email,code)
            if not self.redis_conn.get(redis_key):
                self.set_status(400)
                re_data["code"] = "验证码错误或者失效"
            else:
                try:
                    existed_user = await self.application.objects.get(User,Email=email)
                    self.set_status(400)
                    re_data["email"] = "该邮箱已注册"
                except User.DoesNotExist as e:
                    user = await self.application.objects.create(User,Email=email,Password=password,NickName=email)
                    re_data["id"] = user.id
        else:
            self.set_status(400)
            for field in register_form.errors:
                re_data[field] = register_form[field][0]

        self.finish(re_data)

class LoginHandler(RedisHandler):
    async def post(self, *args, **kwargs):
        re_data = {}

        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        form = LoginForm.from_json(param)

        if form.validate():
            email = form.email.data
            password = form.password.data

            try:
                user = await self.application.objects.get(User, Email=email)
                if not user.Password.check_password(password):
                    self.set_status(400)
                    re_data["non_fields"] = "用户名或密码错误"
                else: # login success and write info into jwt

                    payload = {
                        "id" : user.id,
                        "nick_name" : user.NickName,
                        "exp" : datetime.utcnow()
                    }
                    token = jwt.encode(payload, self.settings["secret_key"], algorithm='HS256')
                    re_data["id"] = user.id
                    if user.NickName is not None:
                        re_data["nick_name"] = user.NickName
                    else:
                        re_data["nick_name"] = user.Email
                    re_data["token"] = token.decode("utf-8")

            except User.DoesNotExist as e:
                self.set_status(400)
                re_data["email"] = "用户不存在"

            self.finish(re_data)

class ProfileHandler(RedisHandler):
    @authenticated_async
    async def get(self, *args, **kwargs):
        re_data = {
            "email":self.current_user.Email,
            "nick_name":self.current_user.NickName,
            "gender":self.current_user.Gender,
            "desc":self.current_user.Desc
        }
        self.finish(re_data)

    @authenticated_async
    async def patch(self, *args, **kwargs):
        re_data = {}
        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        profile_form = ProfileForm.from_json(param)
        if profile_form.validate():
            self.current_user.NickName = profile_form.nick_name.data
            self.current_user.Gender = profile_form.gender.data
            self.current_user.Desc = profile_form.desc.data

            await self.application.objects.update(self.current_user)
        else:
            self.set_status(400)
            for field in profile_form.errors:
                re_data[field] = profile_form.errors[field][0]

        self.finish(re_data)

class HeadImageHandler(RedisHandler):

    @authenticated_async
    async def get(self, *args, **kwargs):
        self.finish({
            "image":"/media/" + self.current_user.HeadUrl
        })

    @authenticated_async
    async def post(self, *args, **kwargs):
        re_data = {}

        files_meta = self.request.files.get("image", None)
        if not files_meta:
            self.set_status(400)
            re_data["image"]="请上传图片"
        else:
            # save image and set log
            # write file by aiofiles
            new_filename = ""
            for meta in files_meta:
                filename = meta["filename"]
                new_filename = "{uuid}_{filename}".format(uuid=uuid.uuid1(),filename=filename)
                file_path = os.path.join(self.settings["MEDIA_ROOT"], new_filename)
                async with aiofiles.open(file_path,'wb') as f:
                    await f.write(meta['body'])
                    re_data["image"] = "/media/" + new_filename

                self.current_user.HeadUrl = new_filename
                await self.application.objects.update(self.current_user)

        self.finish(re_data)

class ChangePasswordHandler(RedisHandler):
    @authenticated_async
    async def post(self, *args, **kwargs):
        # change password
        re_data = {}
        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        password_form = ChangePasswordForm.from_json(param)
        if password_form.validate():
            # check old password
            if not self.current_user.Password.check_password(password_form.old_password.data):
                self.set_status(400)
                re_data["old_password"] = "旧密码错误"
            else:
                if password_form.new_password.data != password_form.confirm_password.data:
                    self.set_status(400)
                    re_data["old_password"] = "两次密码不一致"
                else:
                    self.current_user.Password = password_form.new_password.data
                    await self.application.objects.update(self.current_user)
        else:
            self.set_status(400)
            for field in password_form.errors:
                re_data[field] = password_form.errors[field][0]

        self.finish(re_data)