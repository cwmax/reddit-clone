import datetime
import pickle

import snappy


class RedisCacheHelper():
    def __init__(self, redis):
        self.redis = redis
        self.ttl = datetime.timedelta(days=1)

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

    def commpress_and_ser_mapping(self, mapping):
        try:
            compressed_data = {x: self.serialize_and_compress_data(mapping[x].dict()) for x in mapping}
        except AttributeError:
            compressed_data = {x: self.serialize_and_compress_data(mapping[x]) for x in mapping}
        return compressed_data

    async def hset(self, name, key=None, value=None, mapping=None):
        if value is not None:
            compressed_data = self.serialize_and_compress_data(value)
            await self.redis.hset(name, key, compressed_data)
            await self.redis.expire(name, self.ttl)
        else:
            compressed_data = self.commpress_and_ser_mapping(mapping)
            await self.redis.hset(name, mapping=compressed_data)
            await self.redis.expire(name, self.ttl)

    async def hsetraw(self, name, key=None, value=None, mapping=None):
        await self.redis.hset(name, key, value, mapping)
        await self.redis.expire(name, self.ttl)

    async def hget(self, name, key):
        value = await self.redis.hget(name, key)
        data = None
        if value is not None:
            data = self.deserialize_and_decompress_data(value)
            await self.redis.expire(name, self.ttl)
        return data

    async def hexists(self, name, key):
        return await self.redis.hexists(name, key)

    async def exists(self, name):
        return await self.redis.exists(name)

    async def hgetraw(self, name, key=None):
        val = await self.redis.hget(name, key)
        await self.redis.expire(name, self.ttl)
        if val is not None:
            val = val.decode('utf-8')
        return val

    async def hgetall(self, name):
        values = await self.redis.hgetall(name)
        data = {}
        if len(values) > 0:
            for key in values:
                data[key.decode('utf-8')] = self.deserialize_and_decompress_data(values[key])
            await self.redis.expire(name, self.ttl)
        return data

    async def hgetallraw(self, name):
        values = await self.redis.hgetall(name)
        data = {}
        if len(values) > 0:
            for key in values:
                data[key.decode('utf-8')] = values[key].decode('utf-8')
            await self.redis.expire(name, self.ttl)
        return data

    async def hmget(self, name, keys):
        values = await self.redis.hmget(name, keys=keys)
        data = {}
        for key, value in zip(keys, values):
            if value is None:
                continue
            data[key] = self.deserialize_and_decompress_data(value)
        await self.redis.expire(name, self.ttl)
        return data

    async def set(self, name, value):
        compressed_data = self.serialize_and_compress_data(value)
        await self.redis.set(name, compressed_data)
        await self.redis.expire(name, self.ttl)

    async def get(self, name):
        value = await self.redis.get(name)
        data = None
        if value is not None:
            data = self.deserialize_and_decompress_data(value)
            await self.redis.expire(name, self.ttl)
        return data

    async def hincrby(self, name, key, value):
        return await self.redis.hincrby(name, key, value)
