# PyTexas2017

[![CircleCI](https://circleci.com/gh/tjensen/PyTexas2017.svg?style=shield&circle-token=e8fffca922a554caaf89786ffb4be30a5ea11fa2)](https://circleci.com/gh/tjensen/PyTexas2017)

This repository contains the complete example code from my PyTexas 2017 talk,
"[Building Asynchronous Microservices with Tornado](http://talks.ustud.io/talks/asynchronous-microservices-tornado/)."
The code requires Python 3.6.

## How to Run

Running `run_service.py` will start the example HTTP service, listening on
a port on the localhost interface. I do **not** recommend reconfiguring the
service to listen on a publicly accessible IP. Pressing Ctrl+C should stop the
service.

The following environment variables must be set in order for the service to
run:

* `SERVER_PORT` - This sets the port that the HTTP server will listen on.
* `MONGODB_URI` - The URI of your MongoDB server. Example:
    `mongodb://localhost:12345/mydb`
* `REDIS_HOST` - The hostname or IP of your Redis server.
* `REDIS_PORT` - The port number your Redis server is listening on.
* `MYSQL_HOST` - The hostname or IP of your MySQL server.
* `MYSQL_PORT` - The port number your MySQL server is listening on.
* `MYSQL_DATABASE` - The name of the MySQL database to use. See section about
    MySQL, below.
* `MYSQL_USER` - The username to use when connecting to MySQL.
* `MYSQL_PASSWORD` - The password to use when connecting to MySQL.
* `AWS_S3_BUCKET` - The name of the AWS S3 bucket to use.
* `AWS_S3_OBJECT` - The object key in the AWS S3 bucket to read and write.

### MySQL

The MySQL database must be initialized before running `run_service.py`. To
initialize the database, set the required `MYSQL_*` environment variables
listed above and then run:

```
python service/mysql/initialize.py
```

This script will create the database and table used by the example service.

### AWS S3

The example service will try to read and write a single object in an AWS S3
bucket. It uses [boto3](https://boto3.readthedocs.io) to talk to S3, so it will
use your AWS credentials stored in ~/.aws/credentials, if available. You can
also configure your credentials by setting the `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY` environment variables.
