import os

import tornado.httpserver
import tornado.ioloop
import tornado.web


def main(environ):
    app = tornado.web.Application([])

    server = tornado.httpserver.HTTPServer(app)
    server.listen(int(environ["SERVER_PORT"]))

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main(os.environ)
