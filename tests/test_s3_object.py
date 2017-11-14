import io
import os
import random

import boto3
import tornado.testing

from service.s3_object import S3Object


class TestS3Object(tornado.testing.AsyncTestCase):
    def setUp(self):
        super().setUp()

        self.s3_object = S3Object(os.environ["AWS_S3_BUCKET"], os.environ["AWS_S3_OBJECT"])

        self.expected_contents = f"data-{random.random()}".encode("utf8")

    @tornado.testing.gen_test
    async def test_download_returns_contents_of_s3_object(self):
        boto3.resource("s3").Bucket(os.environ["AWS_S3_BUCKET"]).upload_fileobj(
            Key=os.environ["AWS_S3_OBJECT"],
            Fileobj=io.BytesIO(self.expected_contents))

        contents = await self.s3_object.download()

        self.assertEqual(self.expected_contents, contents)

    @tornado.testing.gen_test
    async def test_upload_sets_contents_of_s3_object(self):
        await self.s3_object.upload(self.expected_contents)

        contents = io.BytesIO()
        boto3.resource("s3").Bucket(os.environ["AWS_S3_BUCKET"]).download_fileobj(
            Key=os.environ["AWS_S3_OBJECT"],
            Fileobj=contents)
        self.assertEqual(self.expected_contents, contents.getvalue())
