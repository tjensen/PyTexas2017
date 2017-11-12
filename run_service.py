import functools
import os

import aiomysql
import aioredis
import boto3
import motor.motor_tornado
import tornado.httpserver
import tornado.ioloop
import tornado.platform.asyncio
import tornado.web

from service.handlers.bart_handler import BartHandler
from service.handlers.flanders_handler import FlandersHandler
from service.handlers.healthcheck_handler import HealthcheckHandler
from service.handlers.homers_handler import HomersHandler
from service.handlers.lisas_handler import LisasHandler
from service.handlers.maggie_handler import MaggieHandler
from service.handlers.marges_handler import MargesHandler


WEATHER_URI = "https://query.yahooapis.com/v1/public/yql?q=select%20item.condition" \
    "%20from%20weather.forecast%20where%20woeid%20%3D%202357536&format=json"


def make_app(config):
    return tornado.web.Application([
        ("/api/v1/bart", BartHandler),
        ("/api/v1/flanders", FlandersHandler),
        ("/api/v1/healthcheck", HealthcheckHandler),
        ("/api/v1/homers/(.*)", HomersHandler),
        ("/api/v1/lisas/(.*)", LisasHandler),
        ("/api/v1/maggie", MaggieHandler),
        ("/api/v1/marges/(.*)", MargesHandler)
    ], **config)


async def connect_redis(environ):
    return await aioredis.create_redis((environ["REDIS_HOST"], environ["REDIS_PORT"]))


async def connect_mysql(environ):
    return await aiomysql.connect(
        host=environ["MYSQL_HOST"], port=int(environ["MYSQL_PORT"]), db=environ["MYSQL_DATABASE"],
        user=environ["MYSQL_USER"], password=environ["MYSQL_PASSWORD"])


def main(environ):
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    ioloop = tornado.ioloop.IOLoop.current()

    motor_client = motor.motor_tornado.MotorClient(environ["MONGODB_URI"])
    mongo_db = motor_client.get_default_database()

    redis = ioloop.run_sync(functools.partial(connect_redis, environ))

    mysql = ioloop.run_sync(functools.partial(connect_mysql, environ))

    s3_bucket = boto3.resource("s3").Bucket(environ["AWS_S3_BUCKET"])

    app = make_app({
        "motor_client": motor_client,
        "mongo_db": mongo_db,
        "redis": redis,
        "mysql": mysql,
        "s3_bucket": s3_bucket,
        "s3_object": environ["AWS_S3_OBJECT"],
        "weather_uri": WEATHER_URI
    })

    server = tornado.httpserver.HTTPServer(app)
    server.listen(int(environ["SERVER_PORT"]), "localhost")

    ioloop.start()


if __name__ == "__main__":
    main(os.environ)
