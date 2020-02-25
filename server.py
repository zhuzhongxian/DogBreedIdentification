from tornado import web
import tornado

from DogBreedIdentification.urls import urlpatten
from DogBreedIdentification.settings import settings

if __name__ == "__main__":
    app = web.Application(urlpatten, debug=True, **settings)
    app.listen(8880)
    tornado.ioloop.IOLoop.current().start()
