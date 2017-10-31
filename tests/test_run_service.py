import unittest
from unittest import mock

import run_service


class TestRunService(unittest.TestCase):
    @mock.patch("tornado.ioloop.IOLoop", autospec=True)
    @mock.patch("tornado.httpserver.HTTPServer", autospec=True)
    @mock.patch("tornado.web.Application", autospec=True)
    @mock.patch("motor.motor_tornado.MotorClient", autospec=True)
    def test_main_starts_service(
            self, mock_motorclient_class, mock_application_class, mock_httpserver_class,
            mock_ioloop_class):
        mock_motorclient = mock_motorclient_class.return_value
        mock_mongo_db = mock_motorclient.get_default_database.return_value
        mock_ioloop = mock_ioloop_class.current.return_value
        mock_httpserver = mock_httpserver_class.return_value

        run_service.main({
            "SERVER_PORT": "8000",
            "MONGODB_URI": "mongodb-uri"
        })

        mock_motorclient_class.assert_called_once_with("mongodb-uri")

        mock_application_class.assert_called_once_with(
            mock.ANY,
            motor_client=mock_motorclient,
            mongo_db=mock_mongo_db)

        mock_httpserver_class.assert_called_once_with(mock_application_class.return_value)
        mock_httpserver.listen.assert_called_once_with(8000)

        mock_ioloop_class.current.assert_called_once_with()
        mock_ioloop.start.assert_called_once_with()
