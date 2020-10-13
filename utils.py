"""
Created by Epic at 10/13/20
"""
from cache import CacheElement

from logging import getLogger

logger = getLogger("AQue.utils")


def cacheable(cache_id, *, expire=10 * 60):
    def outer(func):
        def inner(*args, **kwargs):
            object_id = str(sum([hash(arg) for arg in args]))
            cache = CacheElement(cache_id + "." + object_id, expire=expire)
            cache_value = cache.get()
            if cache_value is None:
                cache_value = func(*args, **kwargs)
                cache.set(cache_value)
            return cache_value

        return inner

    return outer


def remove_cache(cache_id, args):
    object_id = str(sum([hash(arg) for arg in args]))
    cache_path = cache_id + "." + object_id
    cache = CacheElement(cache_path, expire=1)
    cache.set(None)
