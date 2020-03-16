import json
from random import choice
from datetime import datetime
#from functools import partial

from tornado.web import RequestHandler
import jwt

from apps.users.forms import EmailCodeForm,RegisterForm,LoginForm
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