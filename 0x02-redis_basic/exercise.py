#!/usr/bin/env python3
""" 
Redis client module
"""

import redis
import uuid
from typing import Union


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
