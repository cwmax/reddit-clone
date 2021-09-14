import pickle

import snappy


class RedisCacheHelper():
    def __init__(self, redis):
        self.redis = redis

    @staticmethod
    def serialize_and_compress_data(data):
        pickled_data = pickle.dumps(data)
        compressed_data = snappy.compress(pickled_data)
        return compressed_data

    @staticmethod
    def deserialize_and_decompress_data(data):
        decompressed_data = snappy.decompress(data)
        depickled_data = pickle.loads(decompressed_data)
        return depickled_data

    async def hset(self, name, key, value):
        compressed_data = self.serialize_and_compress_data(value)
        await self.redis.hset(name, key, compressed_data)

    async def hget(self, name, key):
        value = await self.redis.hget(name, key)
        data = self.deserialize_and_decompress_data(value)
        return data
