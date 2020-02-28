from tornado.web import url
from apps.search.handler import BreedHandler

urlpattern = (
    url("/breed/", BreedHandler),
)