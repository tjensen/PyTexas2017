import tornado.web


class HealthcheckHandler(tornado.web.RequestHandler):
    async def get(self):
        await tornado.gen.multi([
            self.settings["mongo_db"].command("ping"),
            self.settings["redis"].ping()
        ])

        self.finish("OK")
