import redis
import requests
from functools import wraps
from typing import Callable

redis_client = redis.Redis()

def cache_page(method: Callable) -> Callable:
    """Decorator to cache the result of a page fetch and track the access count."""
    @wraps(method)
    def wrapper(url: str) -> str:

        cache_key = f"cache:{url}"
        count_key = f"count:{url}"
        
        cached_content = redis_client.get(cache_key)
        if cached_content:

            redis_client.incr(count_key)
            return cached_content.decode("utf-8")

        content = method(url)

        redis_client.setex(cache_key, 10, content)

        redis_client.incr(count_key)

        return content

    return wrapper

@cache_page
def get_page(url: str) -> str:
    """Fetch the HTML content of a URL."""
    response = requests.get(url)
    return response.text
