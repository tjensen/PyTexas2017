from unittest import mock

import tornado.concurrent
import tornado.testing

from run_service import make_app


class TestHealthcheckHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        self.mongo_db = mock.Mock()

        return make_app({
            "mongo_db": self.mongo_db
        })

    def future_returning(self, result):
        future = tornado.concurrent.Future()
        future.set_result(result)
        return future

    def future_raising(self, exception):
        future = tornado.concurrent.Future()
        future.set_exception(exception)
        return future

    def test_get_returns_200_when_healthy(self):
        self.mongo_db.command.return_value = self.future_returning({"ok": 1.0})

        response = self.fetch("/api/v1/healthcheck")

        self.assertEqual(200, response.code)
        self.assertEqual("OK", response.body.decode("utf8"))

    def test_get_returns_500_if_mongo_database_is_down(self):
        self.mongo_db.command.return_value = self.future_raising(Exception("error"))

        response = self.fetch("/api/v1/healthcheck")

        self.assertEqual(500, response.code)
