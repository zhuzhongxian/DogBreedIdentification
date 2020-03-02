from tornado.web import url
from apps.search.handler import BreedHandler,BreedDetailHandler,PostHandler

urlpattern = (
    url("/breeds/", BreedHandler),
    url("/breeds/([0-9]+)/",BreedDetailHandler),
    url("/breeds/([0-9]+)/posts/",PostHandler)
)