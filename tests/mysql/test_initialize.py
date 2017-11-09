import os
import unittest
from unittest import mock

import aiomysql
import tornado.gen
import tornado.testing

from run_service import connect_mysql
from service.mysql.initialize import destroy, initialize, main


class TestInitialize(tornado.testing.AsyncTestCase):
    def tearDown(self):
        self.io_loop.run_sync(lambda: destroy(os.environ))

        super().tearDown()

    def get_new_ioloop(self):
        return tornado.platform.asyncio.AsyncIOLoop()

    @tornado.testing.gen_test
    async def test_initialize_creates_database_and_table(self):
        await initialize(os.environ)

        db = await connect_mysql(os.environ)
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


class TestMain(unittest.TestCase):
    @mock.patch("asyncio.get_event_loop")
    @mock.patch("service.mysql.initialize.initialize")
    def test_main_calls_initialize_on_event_loop(self, mock_initialize, mock_get_event_loop):
        main(os.environ)

        mock_initialize.assert_called_once_with(os.environ)
        mock_get_event_loop.assert_called_once_with()
        mock_get_event_loop.return_value.run_until_complete.assert_called_once_with(
            mock_initialize.return_value)
