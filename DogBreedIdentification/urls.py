from tornado.web import url
from tornado.web import StaticFileHandler

from apps.users import urls as user_urls
from apps.search import urls as search_urls
from DogBreedIdentification.settings import settings
urlpattern = [      # for visiting image files
    (url("/media/(.*)", StaticFileHandler, {'path' : settings["MEDIA_ROOT"]}))
]

urlpattern += user_urls.urlpattern
urlpattern += search_urls.urlpattern