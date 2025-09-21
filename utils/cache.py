import time
from functools import lru_cache, wraps

def timed_lru_cache(seconds: int = 300, maxsize: int = 128):
    def wrapper(func):
        @lru_cache(maxsize=maxsize)
        def cached_func(*args, _ts, **kwargs):
            return func(*args, **kwargs)

        @wraps(func)
        def inner(*args, **kwargs):
            ts = int(time.time() // seconds)
            return cached_func(*args, _ts=ts, **kwargs)
        inner.cache_clear = cached_func.cache_clear  # type: ignore[attr-defined]
        return inner
    return wrapper