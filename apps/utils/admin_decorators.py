import functools


from apps.admin.models import Admin
def admin_pre(method):
    """Decorate methods with this to require that the user be logged in.

    If the user is not logged in, they will be redirected to the configured
    `login url <RequestHandler.get_login_url>`.

    If you configure a login url with a query parameter, Tornado will
    assume you know what you're doing and use it as-is.  If not, it
    will add a `next` parameter so the login page knows where to send
    you once you're logged in.
    """

    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        token = self.request.headers.get("sessionid",None)
        if token:
            admin_id = token.split("_")
            id=admin_id[0]

            try:
                admin = await self.application.objects.get(Admin, id=id)
                #if not user['NickName']:
                    #user['NickName'] = user['Email']
                self._current_user = admin
                # function
                await method(self, *args, **kwargs)
            except Admin.DoesNotExist as e:
                self.set_status(401)

        else:
            self.set_status(401)
        #self.finish({})

    return wrapper
