from unittest import mock

import tornado.testing

import run_service
from tests.helpers import future_returning


class TestRunService(tornado.testing.AsyncTestCase):
    @mock.patch("tornado.ioloop.IOLoop")
    @mock.patch("functools.partial", autospec=True)
    @mock.patch("tornado.platform.asyncio.AsyncIOMainLoop", autospec=True)
    @mock.patch("tornado.httpserver.HTTPServer", autospec=True)
    @mock.patch("tornado.web.Application", autospec=True)
    @mock.patch("run_service.S3Object", autospec=True)
    @mock.patch("run_service.connect_mysql", autospec=True)
    @mock.patch("run_service.connect_redis", autospec=True)
    @mock.patch("motor.motor_tornado.MotorClient", autospec=True)
    def test_main_starts_service(
            self, mock_motorclient_class, mock_connect_redis, mock_connect_mysql,
            mock_s3_object_class, mock_application_class, mock_httpserver_class,
            mock_asynciomainloop_class, mock_partial, mock_ioloop_class):

        mock_motorclient = mock_motorclient_class.return_value
        mock_mongo_db = mock_motorclient.get_default_database.return_value
        mock_httpserver = mock_httpserver_class.return_value
        mock_asynciomainloop = mock_asynciomainloop_class.return_value
        mock_ioloop = mock_ioloop_class.current.return_value
        mock_s3_object = mock_s3_object_class.return_value

        mock_redis = mock.Mock()
        mock_mysql = mock.Mock()
        mock_ioloop.run_sync.side_effect = [
            mock_redis,
            mock_mysql
        ]

        mock_connect_redis_partial = mock.Mock()
        mock_connect_mysql_partial = mock.Mock()
        mock_partial.side_effect = [
            mock_connect_redis_partial,
            mock_connect_mysql_partial
        ]

        environ = {
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
        }

        run_service.main(environ)

        mock_asynciomainloop_class.assert_called_once_with()
        mock_asynciomainloop.install.assert_called_once_with()
        mock_ioloop_class.current.assert_called_once_with()

        mock_motorclient_class.assert_called_once_with("mongodb-uri")

        self.assertCountEqual(
            [
                mock.call(mock_connect_redis, environ),
                mock.call(mock_connect_mysql, environ)
            ],
            mock_partial.call_args_list)
        self.assertCountEqual(
            [
                mock.call(mock_connect_redis_partial),
                mock.call(mock_connect_mysql_partial)
            ],
            mock_ioloop.run_sync.call_args_list)

        mock_s3_object_class.assert_called_once_with("aws-s3-bucket", "aws-s3-object")

        mock_application_class.assert_called_once_with(
            mock.ANY,
            motor_client=mock_motorclient,
            mongo_db=mock_mongo_db,
            redis=mock_redis,
            mysql=mock_mysql,
            s3_object=mock_s3_object,
            weather_uri=run_service.WEATHER_URI)

        mock_httpserver_class.assert_called_once_with(mock_application_class.return_value)
        mock_httpserver.listen.assert_called_once_with(8000, "localhost")

        mock_ioloop.start.assert_called_once_with()

    @mock.patch("aioredis.create_redis", autospec=True)
    @tornado.testing.gen_test
    async def test_connect_redis_connects_to_redis(self, mock_create_redis):
        expected_result = mock.Mock()

        mock_create_redis.return_value = future_returning(expected_result)

        result = await run_service.connect_redis({
            "REDIS_HOST": "redis-host",
            "REDIS_PORT": "redis-port"
        })

        self.assertEqual(expected_result, result)

        mock_create_redis.assert_called_once_with(("redis-host", "redis-port"))

    @mock.patch("aiomysql.connect", autospec=True)
    @tornado.testing.gen_test
    async def test_connect_mysql_connects_to_mysql(self, mock_connect):
        expected_result = mock.Mock()

        mock_connect.return_value = future_returning(expected_result)

        result = await run_service.connect_mysql({
            "MYSQL_HOST": "mysql-host",
            "MYSQL_PORT": "5555",
            "MYSQL_DATABASE": "mysql-database",
            "MYSQL_USER": "mysql-user",
            "MYSQL_PASSWORD": "mysql-password"
        })

        self.assertEqual(expected_result, result)

        mock_connect.assert_called_once_with(
            host="mysql-host", port=5555, db="mysql-database", user="mysql-user",
            password="mysql-password")
