from tornado.web import url
from apps.users.handler import EmailCodeHandler,RegisterHandler,LoginHandler,ProfileHandler,HeadImageHandler,ChangePasswordHandler,FollowsHandler

urlpattern = (
    url("/code/", EmailCodeHandler),
    url("/register/",RegisterHandler),
    url("/login/",LoginHandler),
    url("/info/",ProfileHandler),
    url("/headimage/",HeadImageHandler),
    url("/password/",ChangePasswordHandler),
    url("/follows/",FollowsHandler),
)