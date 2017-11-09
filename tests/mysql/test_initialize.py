import os
from unittest import mock

import aiomysql
import tornado.gen
import tornado.testing

from service.mysql.initialize import connect, destroy, initialize, main
from tests.helpers import future_returning


class TestInitialize(tornado.testing.AsyncTestCase):
    def tearDown(self):
        self.io_loop.run_sync(lambda: destroy(os.environ))

        super().tearDown()

    def get_new_ioloop(self):
        return tornado.platform.asyncio.AsyncIOLoop()

    @mock.patch("aiomysql.connect")
    @tornado.testing.gen_test
    async def test_connect_connects_to_mysql(self, mock_connect):
        mock_connect.return_value = future_returning(None)

        await connect(os.environ)

        mock_connect.assert_called_once_with(
            host=os.environ["MYSQL_HOST"], port=int(os.environ["MYSQL_PORT"]),
            db=os.environ["MYSQL_DATABASE"], user=os.environ["MYSQL_USER"],
            password=os.environ["MYSQL_PASSWORD"])

    @mock.patch("aiomysql.connect")
    @tornado.testing.gen_test
    async def test_connect_connects_to_mysql_without_db_when_use_database_is_false(
            self, mock_connect):
        mock_connect.return_value = future_returning(None)

        await connect(os.environ, use_database=False)

        mock_connect.assert_called_once_with(
            host=os.environ["MYSQL_HOST"], port=int(os.environ["MYSQL_PORT"]),
            user=os.environ["MYSQL_USER"], password=os.environ["MYSQL_PASSWORD"])

    @tornado.testing.gen_test
    async def test_initialize_creates_database_and_table(self):
        await initialize(os.environ)

        db = await connect(os.environ)
        try:
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("DESCRIBE lisa;")

                self.assertCountEqual(
                    [
                        {
                            "Field": "name",
                            "Type": "varchar(32)",
                            "Key": "PRI",
                            "Default": None,
                            "Null": "NO",
                            "Extra": ""
                        },
                        {
                            "Field": "content",
                            "Type": "varchar(1000)",
                            "Key": "",
                            "Default": None,
                            "Null": "NO",
                            "Extra": ""
                        }
                    ],
                    await cursor.fetchall())
        finally:
            db.close()

    @mock.patch("asyncio.get_event_loop")
    @mock.patch("service.mysql.initialize.initialize")
    @tornado.testing.gen_test
    async def test_main_calls_initialize_on_event_loop(self, mock_initialize, mock_get_event_loop):
        main(os.environ)

        mock_initialize.assert_called_once_with(os.environ)
        mock_get_event_loop.assert_called_once_with()
        mock_get_event_loop.return_value.run_until_complete.assert_called_once_with(
            mock_initialize.return_value)
