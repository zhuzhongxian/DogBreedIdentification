import peewee_async

settings = {
    "static_path" : "",
    "static_url_prefix" : "",
    "template_path" : "",
    "secret_key" : "zXg&z50C3RGRsLy$",
    "jwt_expire" : 7 * 24 * 3600,
    "db" : {
        "host" : "127.0.0.1",
        "user" : "root",
        "password" : "123456",
        "name" : "dogbreedidentification",
        "port" : 3306
    },
    "redis" : {
        "host" : "127.0.0.1"
    }
}

database = peewee_async.MySQLDatabase(
    'dogbreedidentification',
    host = "127.0.0.1",
    port = 3306,
    user = "root",
    password = "123456"
)
