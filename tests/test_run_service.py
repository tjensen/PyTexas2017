import unittest
from unittest import mock

import run_service


class TestRunService(unittest.TestCase):
    @mock.patch("asyncio.get_event_loop")
    @mock.patch("tornado.platform.asyncio.AsyncIOMainLoop", autospec=True)
    @mock.patch("tornado.httpserver.HTTPServer", autospec=True)
    @mock.patch("tornado.web.Application", autospec=True)
    @mock.patch("boto3.resource")
    @mock.patch("aiomysql.connect")
    @mock.patch("aioredis.create_redis")
    @mock.patch("motor.motor_tornado.MotorClient", autospec=True)
    def test_main_starts_service(
            self, mock_motorclient_class, mock_create_redis, mock_connect, mock_resource,
            mock_application_class, mock_httpserver_class, mock_asynciomainloop_class,
            mock_get_event_loop):

        mock_motorclient = mock_motorclient_class.return_value
        mock_mongo_db = mock_motorclient.get_default_database.return_value
        mock_httpserver = mock_httpserver_class.return_value
        mock_asynciomainloop = mock_asynciomainloop_class.return_value
        mock_eventloop = mock_get_event_loop.return_value
        mock_s3 = mock_resource.return_value
        mock_bucket = mock_s3.Bucket.return_value

        mock_redis = mock.Mock()
        mock_mysql = mock.Mock()
        mock_eventloop.run_until_complete.side_effect = [
            mock_redis,
            mock_mysql
        ]

        run_service.main({
            "SERVER_PORT": "8000",
            "MONGODB_URI": "mongodb-uri",
            "REDIS_HOST": "redis-host",
            "REDIS_PORT": "redis-port",
            "MYSQL_HOST": "mysql-host",
            "MYSQL_PORT": "5555",
            "MYSQL_DATABASE": "mysql-database",
            "MYSQL_USER": "mysql-user",
            "MYSQL_PASSWORD": "mysql-password",
            "AWS_S3_BUCKET": "aws-s3-bucket",
            "AWS_S3_OBJECT": "aws-s3-object"
        })

        mock_asynciomainloop_class.assert_called_once_with()
        mock_asynciomainloop.install.assert_called_once_with()
        mock_get_event_loop.assert_called_once_with()

        mock_motorclient_class.assert_called_once_with("mongodb-uri")

        mock_create_redis.assert_called_once_with(("redis-host", "redis-port"))
        mock_connect.assert_called_once_with(
            host="mysql-host", port=5555, db="mysql-database", user="mysql-user",
            password="mysql-password")
        self.assertCountEqual(
            [
                mock.call(mock_create_redis.return_value),
                mock.call(mock_connect.return_value)
            ],
            mock_eventloop.run_until_complete.call_args_list)

        mock_application_class.assert_called_once_with(
            mock.ANY,
            motor_client=mock_motorclient,
            mongo_db=mock_mongo_db,
            redis=mock_redis,
            mysql=mock_mysql,
            s3_bucket=mock_bucket,
            s3_object="aws-s3-object")

        mock_httpserver_class.assert_called_once_with(mock_application_class.return_value)
        mock_httpserver.listen.assert_called_once_with(8000)

        mock_eventloop.run_forever.assert_called_once_with()
