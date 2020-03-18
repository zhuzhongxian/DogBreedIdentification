import json

from DogBreedIdentification.handler import RedisHandler
from apps.utils.re_decorators import authenticated_async
from apps.message.models import Message
from apps.users.models import User

class MessageHandler(RedisHandler):
    # get messages
    @authenticated_async
    async def get(self, *args, **kwargs):
        re_data = []
        type_list = self.get_query_arguments("message_type",[])
        if type_list:
            message_query = Message.filter(Message.Receiver_id==self.current_user.id,Message.MessageType.in_(type_list))
        else:
            message_query = Message.filter(Message.Receiver_id==self.current_user.id)

        messages = await self.application.objects.execute(message_query)
        for message in messages:
            sender = await self.application.objects.get(User,id=message.Sender_id)
            re_data.append({
                "sender" : {
                    "id":sender.id,
                    "nick_name":sender.NickName,
                    "head_url":"/media/"+sender.HeadUrl
                },
                "message":message.Message,
                "message_type":message.MessageType,
                "parent_content":message.ParentContent,
                "add_time":message.add_time.strftime("%Y-%m-%d %H:%M:%S")
            })

        self.finish(json.dumps(re_data))

