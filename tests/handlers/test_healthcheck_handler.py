import tornado.testing

from run_service import make_app


class TestHealthcheckHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app({})

    def test_get_returns_200_when_healthy(self):
        response = self.fetch("/api/v1/healthcheck")

        self.assertEqual(200, response.code)
        self.assertEqual("OK", response.body.decode("utf8"))
