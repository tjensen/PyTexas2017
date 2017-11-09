import os

import tornado.testing

from run_service import make_app, connect_redis
from tests.handlers.handler_test_case import HandlerTestCase


class TestMargesHandler(HandlerTestCase):
    def tearDown(self):
        self.io_loop.run_sync(self.redis.flushdb)

        super().tearDown()

    def get_app(self):
        self.redis = self.io_loop.run_sync(lambda: connect_redis(os.environ))

        return make_app({
            "redis": self.redis
        })

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
