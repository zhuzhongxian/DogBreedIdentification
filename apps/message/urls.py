from tornado.web import url

from apps.message.handler import MessageHandler,DeleteMessageHandler

urlpattern = (
    url("/messages/",MessageHandler),
    url("/messages/([0-9]+)/delete/",DeleteMessageHandler),
)