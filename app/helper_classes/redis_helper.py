import os

import redis


class RedisBaseClass():
    def __init__(self):
        self.redis = redis.Redis(host=os.environ.get('REDIS_HOST'),
                            port=os.environ.get('REDIS_PORT'),
                            db=os.environ.get('REDIS_DB'))