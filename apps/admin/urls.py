from tornado.web import url

from apps.admin.handler import AdminLoginHandler,AdminAccountsHandler,AdminBreedsHandler\
    ,AdminCommentsHandler,ManageCommentsHandler,ManageAccountsHandler,ManageBreedsHandler,ManageImageHandler

urlpattern = (
    url("/admin/login/",AdminLoginHandler),
    url("/accounts/admin/",AdminAccountsHandler),
    url("/accounts/([0-9]+)/manage/",ManageAccountsHandler),
    url("/breeds/admin/",AdminBreedsHandler),
    url("/breeds/([0-9]+)/manage/",ManageBreedsHandler),
    url("/breeds/([0-9]+)/image/",ManageImageHandler),
    url("/comments/admin/",AdminCommentsHandler),
    url("/comments/([0-9]+)/manage/",ManageCommentsHandler),
)