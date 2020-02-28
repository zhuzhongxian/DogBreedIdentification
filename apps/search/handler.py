from DogBreedIdentification.handler import RedisHandler
from apps.utils.re_decorators import authenticated_async

class BreedHandler(RedisHandler):

    @authenticated_async
    async def get(self, *args, **wkargs):
        token = self.request.headers.get("token",None)
        pass
