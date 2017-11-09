import json

import tornado.httpclient
import tornado.web


class MaggieHandler(tornado.web.RequestHandler):
    async def get(self):
        client = tornado.httpclient.AsyncHTTPClient()
        response = await client.fetch(self.settings["weather_uri"])

        body = json.loads(response.body)
        condition = body["query"]["results"]["channel"]["item"]["condition"]
        temp = condition["temp"]
        text = condition["text"]

        self.finish(f"Currently {temp} degrees and {text} in Austin, TX")
