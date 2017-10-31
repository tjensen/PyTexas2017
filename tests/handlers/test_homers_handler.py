import json
import os
from unittest import mock

import motor.motor_tornado
import tornado.testing

from run_service import make_app


class TestHomersHandler(tornado.testing.AsyncHTTPTestCase):
    def tearDown(self):
        self.io_loop.run_sync(lambda: self.motor_client.drop_database(self.mongo_db))

        super().tearDown()

    def get_app(self):
        self.motor_client = motor.motor_tornado.MotorClient(os.environ["MONGODB_URI"])
        self.mongo_db = self.motor_client.get_default_database()

        return make_app({
            "motor_client": self.motor_client,
            "mongo_db": self.mongo_db
        })

    async def fetch(self, path, method="GET", body=None):
        # Override AsyncHTTPTestCase's fetch method because it stops the IOLoop
        return await self.http_client.fetch(
            self.get_url(path),
            method=method,
            body=body,
            raise_error=False)

    @tornado.testing.gen_test
    async def test_get_returns_404_when_document_does_not_exist_in_database(self):
        response = await self.fetch("/api/v1/homers/missing")

        self.assertEqual(404, response.code)

    @tornado.testing.gen_test
    async def test_get_returns_document_content_from_database(self):
        await self.mongo_db.homers.insert_one({"name": "doh", "content": {"foo": "bar"}})

        response = await self.fetch("/api/v1/homers/doh")

        self.assertEqual(200, response.code)
        self.assertEqual(
            {
                "foo": "bar"
            },
            json.loads(response.body))

    @tornado.testing.gen_test
    async def test_post_inserts_document_into_database(self):
        response = await self.fetch(
            "/api/v1/homers/duff",
            method="POST",
            body=json.dumps({"something": "some value", "another thing": 42}))

        self.assertEqual(204, response.code)

        self.assertEqual(
            {
                "_id": mock.ANY,
                "name": "duff",
                "content": {
                    "something": "some value",
                    "another thing": 42
                }
            },
            await self.mongo_db.homers.find_one({"name": "duff"}))

    @tornado.testing.gen_test
    async def test_post_replaces_document_in_database_when_name_already_exists(self):
        await self.mongo_db.homers.insert_one({"name": "duff", "content": {}})

        response = await self.fetch(
            "/api/v1/homers/duff",
            method="POST",
            body=json.dumps({"doughnuts": ["sprinkles", "jelly", "plain"]}))

        self.assertEqual(204, response.code)

        self.assertEqual(
            {
                "_id": mock.ANY,
                "name": "duff",
                "content": {
                    "doughnuts": [
                        "sprinkles",
                        "jelly",
                        "plain"
                    ]
                }
            },
            await self.mongo_db.homers.find_one({"name": "duff"}))
