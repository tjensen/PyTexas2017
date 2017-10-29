import os

import tornado.httpserver
import tornado.ioloop
import tornado.web

from service.handlers.healthcheck_handler import HealthcheckHandler


def make_app(config):
    return tornado.web.Application([
        ("/api/v1/healthcheck", HealthcheckHandler)
    ], **config)


def main(environ):
    app = make_app({})

    server = tornado.httpserver.HTTPServer(app)
    server.listen(int(environ["SERVER_PORT"]))

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main(os.environ)
