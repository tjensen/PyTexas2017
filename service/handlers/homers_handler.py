import json

import tornado.web


class HomersHandler(tornado.web.RequestHandler):
    async def get(self, name):
        homer = await self.settings["mongo_db"].homers.find_one(
            {"name": name})

        if homer is None:
            raise tornado.web.HTTPError(
                404, f"Missing homer: {name}")

        self.finish(homer["content"])

    async def post(self, name):
        await self.settings["mongo_db"].homers.replace_one(
            {"name": name},
            {
                "name": name,
                "content": json.loads(self.request.body)
            },
            upsert=True)

        self.set_status(204)
        self.finish()
