import asyncio
import os

import aiomysql
import aioredis
import motor.motor_tornado
import tornado.httpserver
import tornado.platform.asyncio
import tornado.web

from service.handlers.healthcheck_handler import HealthcheckHandler
from service.handlers.homers_handler import HomersHandler
from service.handlers.lisas_handler import LisasHandler
from service.handlers.marges_handler import MargesHandler


def make_app(config):
    return tornado.web.Application([
        ("/api/v1/healthcheck", HealthcheckHandler),
        ("/api/v1/homers/(.*)", HomersHandler),
        ("/api/v1/lisas/(.*)", LisasHandler),
        ("/api/v1/marges/(.*)", MargesHandler)
    ], **config)


def main(environ):
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    event_loop = asyncio.get_event_loop()

    motor_client = motor.motor_tornado.MotorClient(environ["MONGODB_URI"])
    mongo_db = motor_client.get_default_database()

    redis = event_loop.run_until_complete(aioredis.create_redis(
        (environ["REDIS_HOST"], environ["REDIS_PORT"])))
    mysql = event_loop.run_until_complete(aiomysql.connect(
        host=environ["MYSQL_HOST"], port=int(environ["MYSQL_PORT"]), db=environ["MYSQL_DATABASE"],
        user=environ["MYSQL_USER"], password=environ["MYSQL_PASSWORD"]))

    app = make_app({
        "motor_client": motor_client,
        "mongo_db": mongo_db,
        "redis": redis,
        "mysql": mysql
    })

    server = tornado.httpserver.HTTPServer(app)
    server.listen(int(environ["SERVER_PORT"]))

    event_loop.run_forever()


if __name__ == "__main__":
    main(os.environ)
