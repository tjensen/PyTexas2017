import tornado.web


class HealthcheckHandler(tornado.web.RequestHandler):
    async def check_mysql(self):
        cursor = await self.settings["mysql"].cursor()
        try:
            await cursor.execute("SHOW TABLES;")
        finally:
            await cursor.close()

    async def get(self):
        await tornado.gen.multi([
            self.settings["mongo_db"].command("ping"),
            self.settings["redis"].ping(),
            self.check_mysql()
        ])

        self.finish("OK")
