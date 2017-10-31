import os

import aioredis
import tornado.platform.asyncio
import tornado.testing

from run_service import make_app


class TestMargesHandler(tornado.testing.AsyncHTTPTestCase):
    def tearDown(self):
        self.io_loop.run_sync(self.redis.flushdb)

        super().tearDown()

    def get_new_ioloop(self):
        return tornado.platform.asyncio.AsyncIOLoop()

    def get_app(self):
        self.redis = self.io_loop.run_sync(
            lambda: aioredis.create_redis((os.environ["REDIS_HOST"], os.environ["REDIS_PORT"])))

        return make_app({
            "redis": self.redis
        })

    async def fetch(self, path, method="GET", body=None):
        # Override AsyncHTTPTestCase's fetch method because it stops the IOLoop
        return await self.http_client.fetch(
            self.get_url(path),
            method=method,
            body=body,
            raise_error=False)

    @tornado.testing.gen_test
    async def test_get_returns_404_when_key_does_not_exist_in_redis(self):
        response = await self.fetch("/api/v1/marges/hair")

        self.assertEqual(404, response.code)

    @tornado.testing.gen_test
    async def test_get_returns_value_when_key_exists_in_redis(self):
        await self.redis.set("hair", "blue")

        response = await self.fetch("/api/v1/marges/hair")

        self.assertEqual(200, response.code)
        self.assertEqual(b"blue", response.body)

    @tornado.testing.gen_test
    async def test_post_sets_value_in_redis(self):
        await self.redis.set("dress", "red")

        response = await self.fetch(
            "/api/v1/marges/dress",
            method="POST",
            body="green")

        self.assertEqual(204, response.code)

        self.assertEqual(b"green", await self.redis.get("dress"))
