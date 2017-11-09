from unittest import mock

import tornado.concurrent
import tornado.testing

from run_service import make_app
from tests.helpers import future_returning, future_raising


class TestHealthcheckHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        self.mongo_db = mock.Mock()
        self.redis = mock.Mock()
        self.mysql = mock.Mock()

        return make_app({
            "mongo_db": self.mongo_db,
            "redis": self.redis,
            "mysql": self.mysql
        })

    def mysql_execute_returning(self, result):
        mysql_cursor = mock.Mock()
        mysql_cursor.execute.return_value = future_returning(result)
        mysql_cursor.close.return_value = future_returning(None)

        self.mysql.cursor.return_value = future_returning(mysql_cursor)

        return mysql_cursor

    def mysql_execute_raising(self, exception):
        mysql_cursor = mock.Mock()
        mysql_cursor.execute.return_value = future_raising(exception)
        mysql_cursor.close.return_value = future_returning(None)

        self.mysql.cursor.return_value = future_returning(mysql_cursor)

        return mysql_cursor

    def test_get_returns_200_when_healthy(self):
        self.mongo_db.command.return_value = future_returning({"ok": 1.0})
        self.redis.ping.return_value = future_returning(b"PONG")
        mysql_cursor = self.mysql_execute_returning(None)

        response = self.fetch("/api/v1/healthcheck")

        self.assertEqual(200, response.code)
        self.assertEqual("OK", response.body.decode("utf8"))

        self.mongo_db.command.assert_called_once_with("ping")

        self.redis.ping.assert_called_once_with()

        self.mysql.cursor.assert_called_once_with()
        mysql_cursor.execute.assert_called_once_with("SHOW TABLES;")
        mysql_cursor.close.assert_called_once_with()

    def test_get_returns_500_if_mongo_database_is_down(self):
        self.mongo_db.command.return_value = future_raising(Exception("mongo error"))
        self.redis.ping.return_value = future_returning(b"PONG")
        self.mysql_execute_returning(None)

        response = self.fetch("/api/v1/healthcheck")

        self.assertEqual(500, response.code)

    def test_get_returns_500_if_redis_is_down(self):
        self.mongo_db.command.return_value = future_returning({"ok": 1.0})
        self.redis.ping.return_value = future_raising(Exception("redis error"))
        self.mysql_execute_returning(None)

        response = self.fetch("/api/v1/healthcheck")

        self.assertEqual(500, response.code)

    def test_get_returns_500_if_mysql_is_down(self):
        self.mongo_db.command.return_value = future_returning({"ok": 1.0})
        self.redis.ping.return_value = future_returning(b"PONG")
        mysql_cursor = self.mysql_execute_raising(Exception("mysql error"))

        response = self.fetch("/api/v1/healthcheck")

        self.assertEqual(500, response.code)

        mysql_cursor.close.assert_called_once_with()
