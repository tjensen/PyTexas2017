import unittest
from unittest import mock

import run_service


class TestRunService(unittest.TestCase):
    @mock.patch("tornado.ioloop.IOLoop", autospec=True)
    @mock.patch("tornado.httpserver.HTTPServer", autospec=True)
    @mock.patch("tornado.web.Application", autospec=True)
    def test_main_starts_service(
            self, mock_application_class, mock_httpserver_class, mock_ioloop_class):
        mock_ioloop = mock_ioloop_class.current.return_value
        mock_httpserver = mock_httpserver_class.return_value

        run_service.main({
            "SERVER_PORT": "8000"
        })

        mock_application_class.assert_called_once_with([])

        mock_httpserver_class.assert_called_once_with(mock_application_class.return_value)
        mock_httpserver.listen.assert_called_once_with(8000)

        mock_ioloop_class.current.assert_called_once_with()
        mock_ioloop.start.assert_called_once_with()
