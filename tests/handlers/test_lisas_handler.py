import os

import aiomysql
import tornado.testing

from run_service import make_app, connect_mysql
from service.mysql.initialize import destroy, initialize
from tests.handlers.handler_test_case import HandlerTestCase


class TestLisasHandler(HandlerTestCase):
    def tearDown(self):
        self.io_loop.run_sync(lambda: self.teardown_database(self.mysql))

        super().tearDown()

    def get_app(self):
        self.mysql = self.io_loop.run_sync(self.setup_database)

        return make_app({
            "mysql": self.mysql
        })

    async def setup_database(self):
        await initialize(os.environ)
        return await connect_mysql(os.environ)

    async def teardown_database(self, db):
        db.close()
        await destroy(os.environ)

    @tornado.testing.gen_test
    async def test_get_returns_404_when_key_does_not_exist_in_mysql(self):
        response = await self.fetch("/api/v1/lisas/saxophone")

        self.assertEqual(404, response.code)

    @tornado.testing.gen_test
    async def test_get_returns_content_when_key_exists_in_mysql(self):
        async with self.mysql.cursor() as cursor:
            await cursor.execute("INSERT INTO lisa (name, content) VALUES ('saxophone', 'music');")

        response = await self.fetch("/api/v1/lisas/saxophone")

        self.assertEqual(200, response.code)
        self.assertEqual(b"music", response.body)

    @tornado.testing.gen_test
    async def test_post_inserts_row_into_mysql(self):
        response = await self.fetch(
            "/api/v1/lisas/dress",
            method="POST",
            body="red")

        self.assertEqual(204, response.code)

        async with self.mysql.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM lisa;")

            self.assertEqual(
                [
                    {"name": "dress", "content": "red"}
                ],
                await cursor.fetchall())

    @tornado.testing.gen_test
    async def test_post_updates_existing_row_in_mysql(self):
        async with self.mysql.cursor() as cursor:
            await cursor.execute("INSERT INTO lisa (name, content) VALUES ('braces', 'off');")

        response = await self.fetch(
            "/api/v1/lisas/braces",
            method="POST",
            body="on")

        self.assertEqual(204, response.code)

        async with self.mysql.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM lisa;")

            self.assertEqual(
                [
                    {"name": "braces", "content": "on"}
                ],
                await cursor.fetchall())
