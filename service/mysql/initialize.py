import asyncio
import os

import aiomysql


async def connect(environ, use_database=True):
    kwargs = {
        "host": environ["MYSQL_HOST"],
        "port": int(environ["MYSQL_PORT"]),
        "user": environ["MYSQL_USER"],
        "password": environ["MYSQL_PASSWORD"]
    }

    if use_database:
        kwargs["db"] = environ["MYSQL_DATABASE"]

    return await aiomysql.connect(**kwargs)


async def initialize(environ):
    db = await connect(environ, use_database=False)
    try:
        async with db.cursor() as cursor:
            await cursor.execute(f"CREATE DATABASE {environ['MYSQL_DATABASE']};")
            await cursor.execute(f"""\
CREATE TABLE {environ['MYSQL_DATABASE']}.lisa (
    name VARCHAR(32) NOT NULL,
    content VARCHAR(1000) NOT NULL,
    PRIMARY KEY (name)
);""")
    finally:
        db.close()


async def destroy(environ):
    db = await connect(environ, use_database=False)
    try:
        async with db.cursor() as cursor:
            await cursor.execute(f"DROP DATABASE IF EXISTS {environ['MYSQL_DATABASE']};")
    finally:
        db.close()


def main(environ):
    asyncio.get_event_loop().run_until_complete(initialize(environ))


if __name__ == "__main__":
    main(os.environ)
