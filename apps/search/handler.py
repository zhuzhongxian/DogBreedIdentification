import json

from playhouse.shortcuts import model_to_dict

from DogBreedIdentification.handler import RedisHandler
from apps.search.forms import PostForm
from apps.utils.re_decorators import authenticated_async
from apps.search.models import DogBreed,Post
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

class PostHandler(RedisHandler):
    @authenticated_async
    async def get(self, breed_id, *args, **kwargs):
        # get post in the breed
        pass

    @authenticated_async
    async def post(self, breed_id, *args, **kwargs):
        re_data = {}

        try:
            breed = await self.application.objects.get(DogBreed, DogIdentifier = int(breed_id))

            param = self.request.body.decode("utf-8")
            param = json.loads(param)
            form = PostForm.from_json(param)
            if form .validate():
                post = await self.application.objects.create(Post, User = self.current_user,
                                                             Content = form.content.data, Breed = breed)
                print(post)
                print(self.current_user)
                re_data["id"] = post.id
            else:
                self.set_status(400)
                for field in form.errors:
                    re_data[field] = form.errors[field][0]
        except DogBreed.DoesNotExist as e:
            self.set_status(404)

        self.finish(re_data)



