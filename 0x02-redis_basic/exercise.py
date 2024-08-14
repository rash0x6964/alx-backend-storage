#!/usr/bin/env python3
""" Redis module """

import functools
from typing import Callable, Optional, Union
from uuid import uuid4
import redis

UnionOfTypes = Union[str, bytes, int, float]


def count_calls(method: Callable) -> Callable:
    """ Decorator to count the number of times a method is called. """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """ Wrap """

        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


class Cache:
    """ Cache redis class """

    def __init__(self):
        """ Constructor of the redis model """

        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: UnionOfTypes) -> str:
        """ Store the input data in Redis using the random key """

        key = str(uuid4())
        self._redis.mset({key: data})
        return key

    def get(self, key: str, fn: Optional[Callable] = None) \
            -> UnionOfTypes:
        """ Convert the data back to the desired format """

        data = self._redis.get(key)
        if data is not None and fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> Optional[str]:
        """ Retrieve the data from Redis and decode it as a UTF-8 string. """
        return self.get(key, lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """ Retrieve the data from Redis and convert it to an integer. """
        return self.get(key, int)
