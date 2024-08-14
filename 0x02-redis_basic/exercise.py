#!/usr/bin/env python3
""" Redis module """

from typing import Union
from uuid import uuid4
import redis

UnionOfTypes = Union[str, bytes, int, float]


class Cache:
    """ Cache redis class """

    def __init__(self):
        """ Constructor of the redis model """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: UnionOfTypes) -> str:
        """
        generate a random key (e.g. using uuid),
         store the input data in Redis using the
          random key and return the key.
        :param data:
        :return:
        """
        key = str(uuid4())
        self._redis.mset({key: data})
        return key
