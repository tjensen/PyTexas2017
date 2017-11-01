import aiomysql
import tornado.web


class LisasHandler(tornado.web.RequestHandler):
    async def get(self, name):
        async with self.settings["mysql"].cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT content FROM lisa where name=%s;", (name,))

            if cursor.rowcount == 0:
                raise tornado.web.HTTPError(404, f"Missing lisa: {name}")

            row = await cursor.fetchone()

            self.finish(row["content"])

    async def post(self, name):
        async with self.settings["mysql"].cursor() as cursor:
            await cursor.execute(
                """\
INSERT INTO lisa (name, content)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE content=%s;""",
                (name, self.request.body, self.request.body))

        self.set_status(204)
        self.finish()
