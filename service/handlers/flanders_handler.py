import tornado.web


class FlandersHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish("Hi-dilly-ho, neighborino!")
