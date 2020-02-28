from tornado import web
import tornado
from peewee_async import Manager

from DogBreedIdentification.urls import urlpattern
from DogBreedIdentification.settings import settings,database

if __name__ == "__main__":

    import wtforms_json
    wtforms_json.init()

    app = web.Application(urlpattern, debug=True, **settings)
    app.listen(8880)

    objects = Manager(database)
    database.set_allow_sync(False) # No need for sync anymore
    app.objects = objects

    tornado.ioloop.IOLoop.current().start()
