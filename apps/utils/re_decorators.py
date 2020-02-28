import functools
import jwt

from apps.users.models import User
def authenticated_async(method):
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
        token = self.request.headers.get("token",None)
        if token:
            try:
                send_data = jwt.decode(token, self.settings["secret_key"],
                                       leeway=self.settings["jwt_expire"],options={"verify_exp" : True})
                user_id = send_data["id"]
                try:
                    user = await self.application.objects.get(User, id=user_id)
                    self._current_user = user
                    # function
                    await method(self, *args, **kwargs)
                except User.DoesNotExist as e:
                    self.set_status(401)
            except jwt.ExpiredSignatureError as e:
                self.set_status(401)
        else:
            self.set_status(401)
        self.finish({})

    return wrapper
