import asyncio
import logging
from functools import wraps
from typing import Any, Callable, Dict, Tuple

logger = logging.getLogger("proxy_decorator")

# --- Simple async cache decorator
class CacheDecorator:
    def __init__(self):
        self._cache: Dict[Tuple, Any] = {}
        self._ttl: Dict[Tuple, float] = {}

    def set_ttl(self, seconds: int):
        self._default_ttl = seconds

    def has(self, command: Any) -> bool:
        key = self._key(command)
        if key in self._cache and time.time() < self._ttl[key]:
            return True
        return False

    def get(self, command: Any) -> Any:
        return self._cache[self._key(command)]

    def set(self, command: Any, value: Any, ttl: int = 60):
        key = self._key(command)
        self._cache[key] = value
        self._ttl[key] = time.time() + ttl

    def _key(self, command: Any) -> Tuple:
        # Pode customizar para usar params do command
        return tuple(sorted(command.__dict__.items()))


# --- Logging decorator
def with_logging(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"Executing {func.__name__} with args={args} kwargs={kwargs}")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"Result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper


# --- Retry decorator
def with_retry(retries: int = 1, delay: float = 0.5):

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    logger.warning(f"Retry {attempt+1}/{retries} for {func.__name__} failed: {e}")
                    await asyncio.sleep(delay)
            raise last_exc
        return wrapper
    return decorator
