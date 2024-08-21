#!/usr/bin/env python3
""" Writing strings to Redis """
from functools import wraps
import redis
import uuid
from typing import Union, Callable, Optional


def count_calls(method: Callable) -> Callable:
    """
        Decorator that counts method calling times
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
            Generates key using method's qualified name
            Increments the call count in Redis
            Call the original method and return its result
            """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """
        Decorator that stores the history of inputs and outputs for a method
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
            Generates keys for (I/O)s
            Stores input args as a str in a Redis list
            Exec the original method
             and gets output then stores it in Redis list
            Returns output
                                                                """
        i_key = "{}:inputs".format(method.__qualname__)
        o_key = "{}:outputs".format(method.__qualname__)

        self._redis.rpush(i_key, str(args))
        output = method(self, *args, **kwargs)

        self._redis.rpush(o_key, str(output))
        return output

    return wrapper


def replay(method: Callable) -> None:
    """
        Displays calls history of a particular function
        Generates keys for inputs/outputs lists
        Retrieves all inputs and outputs from Redis
        prints overall number of calls
        decodes byts to str and formatting the output
    """
    cache = method.__self__
    method_name = method.__qualname__

    i_key = "{}:inputs".format(method.__qualname__)
    o_key = "{}:outputs".format(method.__qualname__)

    inputs = cache._redis.lrange(i_key, 0, -1)
    outputs = cache._redis.lrange(o_key, 0, -1)

    call_count = cache._redis.get(method_name)
    call_count = int(call_count) if call_count else 0

    print("{} was called {} times:".format(method_name, call_count))

    for i, o in zip(inputs, outputs):
        print("{}(*{}) -> {}".format(method_name,
                                     i.decode("utf-8"), o.decode("utf-8")))


class Cache:
    def __init__(self):
        """
            Init Redis client and flush db
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

        @count_calls
        @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
            Generates a random key using uuid
            Stores the data in Redis using the generated key and returned it
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn:
            Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
            Retrieves datas from Redis using key
            Optionally, uses the callable fn for data conversion
            back to desired format
        """
        data = self._redis.get(key)
        if fn:
            return fn(data)

        return data

    def get_str(self, key: str) -> Optional[str]:
        """
            Retrieves data from Redis and convert it into a str
        """
        return self.get(key, lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """
            Retrieves data from Redis and convert it into an int
        """
    return self.get(key, int)
