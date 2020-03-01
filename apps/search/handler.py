import json

from playhouse.shortcuts import model_to_dict

from DogBreedIdentification.handler import RedisHandler
from apps.utils.re_decorators import authenticated_async
from apps.search.models import DogBreed
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

