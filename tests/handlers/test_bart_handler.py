import io
import os
import random

import boto3
import tornado.testing

from run_service import make_app


class TestBartHandler(tornado.testing.AsyncHTTPTestCase):
    def setUp(self):
        self.s3_bucket = boto3.resource("s3").Bucket(os.environ["AWS_S3_BUCKET"])
        self.s3_object = os.environ["AWS_S3_OBJECT"]

        self.expected_content = f"foobar-{random.random()}".encode("utf8")

        super().setUp()

    def get_app(self):
        return make_app({
            "s3_bucket": self.s3_bucket,
            "s3_object": self.s3_object
        })

    def test_get_returns_content_of_s3_object(self):
        self.s3_bucket.upload_fileobj(
            Key=self.s3_object,
            Fileobj=io.BytesIO(self.expected_content))

        response = self.fetch("/api/v1/bart")

        self.assertEqual(200, response.code)
        self.assertEqual(self.expected_content, response.body)

    def test_post_sets_content_of_s3_object(self):
        response = self.fetch(
            "/api/v1/bart",
            method="POST",
            body=self.expected_content)

        self.assertEqual(204, response.code)

        contents = io.BytesIO()
        self.s3_bucket.download_fileobj(
            Key=self.s3_object,
            Fileobj=contents)

        self.assertEqual(self.expected_content, contents.getvalue())
