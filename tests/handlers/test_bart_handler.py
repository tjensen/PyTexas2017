import os
import random

import tornado.testing

from run_service import make_app
from service.s3_object import S3Object
from tests.handlers.handler_test_case import HandlerTestCase


class TestBartHandler(HandlerTestCase):
    def setUp(self):
        self.expected_content = f"foobar-{random.random()}".encode("utf8")

        super().setUp()

    def get_app(self):
        self.s3_object = S3Object(os.environ["AWS_S3_BUCKET"], os.environ["AWS_S3_OBJECT"])

        return make_app({
            "s3_object": self.s3_object
        })

    @tornado.testing.gen_test
    async def test_get_returns_content_of_s3_object(self):
        await self.s3_object.upload(self.expected_content)

        response = await self.fetch("/api/v1/bart")

        self.assertEqual(200, response.code)
        self.assertEqual(self.expected_content, response.body)

    @tornado.testing.gen_test
    async def test_post_sets_content_of_s3_object(self):
        response = await self.fetch(
            "/api/v1/bart",
            method="POST",
            body=self.expected_content)

        self.assertEqual(204, response.code)

        contents = await self.s3_object.download()
        self.assertEqual(self.expected_content, contents)
