#!/usr/bin/env python3
""" Expiring web cache module """

import requests
import redis
import functools


redis_client = redis.Redis()


def cache_and_track(method):
    """ Decorator to cache the result of a method and track URL access. """

    @functools.wraps(method)
    def wrapper(url: str, *args, **kwargs):
        cache_key = url
        count_key = f"count:{url}"
        print(cache_key, " | ", count_key)

        cached_result = redis_client.get(cache_key)
        if cached_result:
            redis_client.incr(count_key)
            return cached_result.decode('utf-8')

        result = method(url, *args, **kwargs)
        redis_client.setex(cache_key, 10, result)
        redis_client.incr(count_key)

        return result

    return wrapper


@cache_and_track
def get_page(url: str) -> str:
    """ Fetch the HTML content of a URL. """

    response = requests.get(url)
    return response.text
