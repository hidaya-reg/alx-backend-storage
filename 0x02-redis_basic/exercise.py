#!/usr/bin/env python3
""" 
Redis client module
"""

import redis
import uuid
from typing import Union, Callable, Optional
import functools


def count_calls(method: Callable) -> Callable:
	"""Decorator to count how many times a method is scalled"""
	@functools.wraps(method)
	def wrapper(self, *args, **kwargs):
		key = method.__qualname__
		self._redis.incr(key)
		return method(self, *args, **kwargs)
	return wrapper

def call_history(method: Callable) -> Callable:
	"""Decorator to store history of inputs and outputs for a method"""
	@functools.wraps(method)
	def wrapper(self, *args, **kwargs):
		input_key = f"{method.__qualname__}:inputs"
		output_key = f"{method.__qualname__}:outputs"
		self._redis.rpush(input_key, str(args))
		output = method(self, *args, **kwargs)
		self._redis.rpush(output_key, str(output))
		return output
	return wrapper

def replay(method: Callable) -> None:
	""" Display the history of calls for a particular method"""
	redis_instance = method.__self__._redis
	input_key = f"{method.__qualname__}:inputs"
	output_key = f"{method.__qualname__}:outputs"
	inputs = redis_instance.lrange(input_key, 0, -1)
	outputs = redis_instance.lrange(output_key, 0, -1)
	print(f"{method.__qualname__} was called {len(inputs)} times:")
	for input_val, output_val in zip(inputs, outputs):
		print(f"{method.__qualname__}(*{input_val.decode('utf-8')}) -> {output_val.decode('utf-8')}")

class Cache:
	def __init__(self):
		"""Initialize Cache class and flush Redis db"""
		self._redis = redis.Redis()
		self._redis.flushdb()

	@count_calls
	@call_history
	def store(self, data: Union[str, bytes, int, float]) -> str:
		"""Store input data with random key"""
		key = str(uuid.uuid4())
		self._redis.set(key, data)
		return key

	def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
		"""Retrieve data from Redis and optionally apply a conversion fct"""
		value = self._redis.get(key)
		if value is None:
			return None
		if fn:
			return fn(value)
		return value

	def get_str(self, key: str) -> Optional[str]:
		"""Retrieve data from Redis and decode it as UTF-8 string"""
		return self.get(key, fn=lambda d: d.decode("utf-8"))

	def get_int(self, key: str) -> Optional[int]:
		"""Retrieve data from Redis and convert it to an integer"""
		return self.get(key, fn=int)
