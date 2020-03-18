from tornado.web import url

from apps.message.handler import MessageHandler

urlpattern = (
    url("/messages/",MessageHandler),
)