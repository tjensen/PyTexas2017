import concurrent.futures
import io

import tornado.concurrent
import tornado.platform.asyncio
import tornado.web


class BartHandler(tornado.web.RequestHandler):
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    @tornado.concurrent.run_on_executor
    def _upload(self):
        contents = io.BytesIO(self.request.body)

        self.settings["s3_bucket"].upload_fileobj(
            Key=self.settings["s3_object"],
            Fileobj=contents)

    @tornado.concurrent.run_on_executor
    def _download(self):
        contents = io.BytesIO()

        self.settings["s3_bucket"].download_fileobj(
            Key=self.settings["s3_object"],
            Fileobj=contents)

        return contents.getvalue()

    async def get(self):
        contents = await tornado.platform.asyncio.to_tornado_future(self._download())

        self.finish(contents)

    async def post(self):
        await tornado.platform.asyncio.to_tornado_future(self._upload())

        self.set_status(204)
        self.finish()
