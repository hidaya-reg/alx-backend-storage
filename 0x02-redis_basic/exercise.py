#!/usr/bin/env python3
""" 
Redis client module
"""

import redis
import uuid
from typing import Union, Callable, Optional


class Cache:
	def __init__(self):
		"""Initialize Cache class and flush Redis db"""
		self._redis = redis.Redis()
		self._redis.flushdb()

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
