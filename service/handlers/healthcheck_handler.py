import tornado.web


class HealthcheckHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish("OK")
