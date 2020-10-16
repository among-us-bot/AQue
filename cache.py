"""
Created by Epic at 6/26/20
"""
import config
from redis import Redis
import json
from logging import getLogger

redis_client = Redis(host=config.REDIS_HOST, db=config.REDIS_DB, password=config.REDIS_PASSWORD,
                     username=config.REDIS_USERNAME)
logger = getLogger("AQue.cache")


class CacheElement:
    def __init__(self, key, *, expire: int = None):
        self.key = key
        self.expire = expire

    def set(self, value):
        encoded = json.dumps(value).encode("utf-8")
        redis_client.set(self.key, encoded)
        logger.debug(f"Setting key {self.key} to {value} with expiry time {self.expire}")
        if self.expire is not None:
            redis_client.expire(self.key, self.expire)

    def get(self):
        raw = redis_client.get(self.key)
        if raw is None:
            return None
        decoded = json.loads(raw.decode("utf-8"))
        return decoded
