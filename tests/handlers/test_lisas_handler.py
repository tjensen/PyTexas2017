import os

import aiomysql
import tornado.platform.asyncio
import tornado.testing

from run_service import make_app


class TestLisasHandler(tornado.testing.AsyncHTTPTestCase):
    def tearDown(self):
        self.io_loop.run_sync(lambda: self.teardown_database(self.mysql))

        super().tearDown()

    async def setup_database(self):
        db = await aiomysql.connect(
            host=os.environ["MYSQL_HOST"], port=int(os.environ["MYSQL_PORT"]),
            user=os.environ["MYSQL_USER"], password=os.environ["MYSQL_PASSWORD"])
        async with db.cursor() as cursor:
            await cursor.execute(f"CREATE DATABASE {os.environ['MYSQL_DATABASE']}")
        db.close()

        db = await aiomysql.connect(
            host=os.environ["MYSQL_HOST"], port=int(os.environ["MYSQL_PORT"]),
            db=os.environ["MYSQL_DATABASE"], user=os.environ["MYSQL_USER"],
            password=os.environ["MYSQL_PASSWORD"])
        async with db.cursor() as cursor:
            await cursor.execute("""\
CREATE TABLE lisa (
    name VARCHAR(32) NOT NULL,
    content VARCHAR(1000) NOT NULL,
    PRIMARY KEY (name)
);""")
        return db

    async def teardown_database(self, db):
        db.close()

        db = await aiomysql.connect(
            host=os.environ["MYSQL_HOST"], port=int(os.environ["MYSQL_PORT"]),
            user=os.environ["MYSQL_USER"], password=os.environ["MYSQL_PASSWORD"])
        async with db.cursor() as cursor:
            await cursor.execute(f"DROP DATABASE {os.environ['MYSQL_DATABASE']}")
        db.close()

    def get_new_ioloop(self):
        return tornado.platform.asyncio.AsyncIOLoop()

    def get_app(self):
        self.mysql = self.io_loop.run_sync(self.setup_database)

        return make_app({
            "mysql": self.mysql
        })

    async def fetch(self, path, method="GET", body=None):
        # Override AsyncHTTPTestCase's fetch method because it stops the IOLoop
        return await self.http_client.fetch(
            self.get_url(path),
            method=method,
            body=body,
            raise_error=False)

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
