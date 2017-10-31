import tornado.web


class HealthcheckHandler(tornado.web.RequestHandler):
    async def get(self):
        await self.settings["mongo_db"].command("ping")

        self.finish("OK")
