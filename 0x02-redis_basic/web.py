#!/usr/bin/env python3
""" Implementing an expiring web cache and tracker """
import redis
import requests
from functools import wraps
from typing import Callable

credis = redis.Redis()


def cacher(method: Callable) -> Callable:
    """
        Decorator that caches result of method and tracks number of accesses.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        """
            Wrapper method for content caching
                                                                """
        credis.incr("count:{}".format(url))
        cached_content = credis.get("content:{}".format(url))
        if cached_content:
            return cached_content.decode('utf-8')

        content = method(url)
        credis.set("count:{}".format(url), 0)
        credis.setex("content:{}".format(url), 10, content)
        return content
    return wrapper


@cacher
def get_page(url: str) -> str:
    """
        Fetches content from a specefied URL
    """
    res = requests.get(url)
    res.raise_for_status()
    return res.text
