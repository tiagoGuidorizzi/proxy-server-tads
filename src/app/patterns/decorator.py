import time
import functools
import inspect


class CacheDecorator:
    """Decorator de cache com TTL (time-to-live)."""

    def __init__(self, ttl: int = 60):
        self.ttl = ttl
        self._cache = {}

    def __call__(self, func):
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                key = self._make_key(args, kwargs)
                if key in self._cache:
                    data, expiry = self._cache[key]
                    if expiry > time.time():
                        return data
                    else:
                        del self._cache[key]

                result = await func(*args, **kwargs)
                self._cache[key] = (result, time.time() + self.ttl)
                return result
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                key = self._make_key(args, kwargs)
                if key in self._cache:
                    data, expiry = self._cache[key]
                    if expiry > time.time():
                        return data
                    else:
                        del self._cache[key]

                result = func(*args, **kwargs)
                self._cache[key] = (result, time.time() + self.ttl)
                return result

        return wrapper

    def _make_key(self, args, kwargs):
        """Cria uma chave única baseada nos argumentos da função."""
        return str(args) + str(kwargs)
