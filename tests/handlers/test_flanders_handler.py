import tornado.testing

from run_service import make_app


class TestFlandersHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app({})

    def test_get_returns_200_and_greeting(self):
        response = self.fetch("/api/v1/flanders")

        self.assertEqual(200, response.code)
        self.assertEqual("Hi-dilly-ho, neighborino!", response.body.decode("utf8"))
