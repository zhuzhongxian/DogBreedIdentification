from tornado.web import url

from apps.admin.handler import AdminLoginHandler,AdminAccountsHandler,AdminBreedsHandler,AdminCommentsHandler,ManageCommentsHandler

urlpattern = (
    url("/admin/login/",AdminLoginHandler),
    url("/accounts/admin/",AdminAccountsHandler),
    url("/breeds/admin/",AdminBreedsHandler),
    url("/comments/admin/",AdminCommentsHandler),
    url("/comments/([0-9]+)/manage/",ManageCommentsHandler),
)