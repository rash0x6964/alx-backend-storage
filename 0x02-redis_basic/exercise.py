#!/usr/bin/env python3
""" Redis module """

import functools
from typing import Callable, Optional, Union
from uuid import uuid4
import redis

UnionOfTypes = Union[str, bytes, int, float]


def call_history(method: Callable) -> Callable:
    """ Decorator to store the history of inputs and outputs of a function. """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """ Wrap """
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        self._redis.rpush(input_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(output))

        return output

    return wrapper


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
    @call_history
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


def replay(method: Callable) -> None:
    """ Display the history of calls for a particular function. """

    redis_client = method.__self__._redis

    input_key = f"{method.__qualname__}:inputs"
    output_key = f"{method.__qualname__}:outputs"

    inputs = redis_client.lrange(input_key, 0, -1)
    outputs = redis_client.lrange(output_key, 0, -1)

    print(f"{method.__qualname__} was called {len(inputs)} times:")

    for input_val, output_val in zip(inputs, outputs):
        input_str = input_val.decode('utf-8')
        output_str = output_val.decode('utf-8')
        print(f"{method.__qualname__}(*{input_str}) -> {output_str}")
