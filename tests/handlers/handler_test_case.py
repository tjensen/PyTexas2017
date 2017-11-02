import tornado.platform.asyncio
import tornado.testing


class HandlerTestCase(tornado.testing.AsyncHTTPTestCase):
    def get_new_ioloop(self):
        return tornado.platform.asyncio.AsyncIOLoop()

    async def fetch(self, path, method="GET", body=None):
        # Override AsyncHTTPTestCase's fetch method because it stops the IOLoop
        return await self.http_client.fetch(
            self.get_url(path),
            method=method,
            body=body,
            raise_error=False)
