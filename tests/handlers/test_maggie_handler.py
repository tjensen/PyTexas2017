import tornado.web

from run_service import make_app
from tests.handlers.handler_test_case import HandlerTestCase


class MockWeatherHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish({
            "query": {
                "count": 1,
                "created": "2017-11-09T17:30:06Z",
                "lang": "en-US",
                "results": {
                    "channel": {
                        "item": {
                            "condition": {
                                "code": "26",
                                "date": "Thu, 09 Nov 2017 10:00 AM CST",
                                "temp": "52",
                                "text": "Cloudy"
                            }
                        }
                    }
                }
            }
        })


class TestMaggieHandler(HandlerTestCase):
    def get_app(self):
        mock_app = tornado.web.Application([("/weather", MockWeatherHandler)])
        socket, self.mock_server_port = tornado.testing.bind_unused_port()

        self.mock_server = tornado.httpserver.HTTPServer(mock_app)
        self.mock_server.add_sockets([socket])

        return make_app({
            "weather_uri": f"http://localhost:{self.mock_server_port}/weather"
        })

    @tornado.testing.gen_test
    async def test_get_returns_current_conditions_from_weather_api(self):
        response = await self.fetch("/api/v1/maggie")

        self.assertEqual(200, response.code)
        self.assertEqual(
            b"Currently 52 degrees and Cloudy in Austin, TX",
            response.body)
