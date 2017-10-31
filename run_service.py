import os

import motor.motor_tornado
import tornado.httpserver
import tornado.ioloop
import tornado.web

from service.handlers.healthcheck_handler import HealthcheckHandler
from service.handlers.homers_handler import HomersHandler


def make_app(config):
    return tornado.web.Application([
        ("/api/v1/healthcheck", HealthcheckHandler),
        ("/api/v1/homers/(.*)", HomersHandler)
    ], **config)


def main(environ):
    motor_client = motor.motor_tornado.MotorClient(environ["MONGODB_URI"])
    mongo_db = motor_client.get_default_database()

    app = make_app({
        "motor_client": motor_client,
        "mongo_db": mongo_db
    })

    server = tornado.httpserver.HTTPServer(app)
    server.listen(int(environ["SERVER_PORT"]))

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main(os.environ)
