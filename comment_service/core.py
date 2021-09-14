import os

from databases import Database
from aioredis import Redis

from .config import Config

config = Config()


def get_database(
        url=config.POSTGRES_URI,
        min_size=config.POSTGRES_MIN_CON,
        max_size=config.POSTGRES_MAX_CON):
    db = Database(
        url=url,
        min_size=min_size,
        max_size=max_size,
    )
    return db


def get_redis_cache():
    redis = Redis(
        host=os.environ.get('REDIS_HOST'),
        port=os.environ.get('REDIS_PORT'),
        db=os.environ.get('REDIS_DB'),
        max_connections=os.environ.get('MAX_REDIS_CONNECTIONS', 10),
    )
    return redis
