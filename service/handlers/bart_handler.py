import tornado.web


class BartHandler(tornado.web.RequestHandler):
    async def get(self):
        contents = await self.settings["s3_object"].download()

        self.finish(contents)

    async def post(self):
        await self.settings["s3_object"].upload(self.request.body)

        self.set_status(204)
        self.finish()
