from tornado.web import url
from apps.users.handler import EmailCodeHandler,RegisterHandler,LoginHandler

urlpatten = (
    url("/code/", EmailCodeHandler),
    url("/register/",RegisterHandler),
    url("/login/",LoginHandler)
)