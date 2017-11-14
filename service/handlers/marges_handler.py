import tornado.web


class MargesHandler(tornado.web.RequestHandler):
    async def get(self, name):
        marge = await self.settings["redis"].get(name)

        if marge is None:
            raise tornado.web.HTTPError(
                404, f"Missing marge: {name}")

        self.finish(marge)

    async def post(self, name):
        await self.settings["redis"].set(name, self.request.body)

        self.set_status(204)
        self.finish()
