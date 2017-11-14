import concurrent.futures
import io

import boto3
import tornado.concurrent


class S3Object(object):
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    def __init__(self, bucket, key):
        self.bucket = boto3.resource("s3").Bucket(bucket)
        self.key = key

    @tornado.concurrent.run_on_executor
    def _download(self):
        contents = io.BytesIO()

        self.bucket.download_fileobj(
            Key=self.key,
            Fileobj=contents)

        return contents.getvalue()

    async def download(self):
        return await tornado.platform.asyncio.to_tornado_future(
            self._download())

    @tornado.concurrent.run_on_executor
    def _upload(self, data):
        self.bucket.upload_fileobj(
            Key=self.key,
            Fileobj=io.BytesIO(data))

    async def upload(self, data):
        await tornado.platform.asyncio.to_tornado_future(
            self._upload(data))
