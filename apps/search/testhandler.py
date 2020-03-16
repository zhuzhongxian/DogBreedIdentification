import json

from playhouse.shortcuts import model_to_dict

from DogBreedIdentification.handler import RedisHandler
from apps.search.forms import BreedCommentForm
from apps.utils.re_decorators import authenticated_async
from apps.users.models import User
from apps.search.models import DogBreed,BreedComment,CommentLike
from apps.utils.util_func import json_serial
class CommentHandler(RedisHandler):
    @authenticated_async
    async def get(self, breed_id, *args, **kwargs):
        # get comments
        re_data = []
        breed = await self.application.objects.get(DogBreed, DogIdentifier=int(breed_id))
        #post_comments = await self.application.objects.select(BreedComment, Breed_id=breed).join(User, on=(BreedComment.User==User.id)).where(BreedComment.Breed_id==breed,BreedComment.ParentComment.is_null(True)).order_by(BreedComment.add_time.desc())
        U1 = User.alias()
        U2 = User.alias()
        post_comments = await self.application.objects.execute(BreedComment.select(BreedComment.Breed_id,U1.id,U1.NickName,U2.id,U2.NickName).join(U1, on=(U1.id==BreedComment.User_id)).switch(BreedComment).join(U2, on=(U2.id==BreedComment.ReplyUser_id)).where(BreedComment.Breed_id==breed,BreedComment.ParentComment.is_null(True)).order_by(BreedComment.add_time.desc()))
        for item in post_comments:
            print(item)
            has_liked = False
            item_dict ={
                "user": model_to_dict(item.User),
                "content": item.Content,
                "reply_nums": item.ReplyNum,
                "like_nums": item.LikeNum,
                "has_liked": has_liked,
                "id": item.id,
            }
            re_data.append(item_dict)

        print(re_data)