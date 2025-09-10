import time


class CacheDecorator:
    def __init__(self, ttl: int = 60):
        self.ttl = ttl
        self._cache = {}

    def has(self, command):
        key = str(command)
        if key in self._cache:
            data, expiry = self._cache[key]
            if expiry > time.time():
                return True
            else:
                del self._cache[key]
        return False

    def get(self, command):
        key = str(command)
        return self._cache[key][0] if key in self._cache else None

    def set(self, command, value):
        key = str(command)
        self._cache[key] = (value, time.time() + self.ttl)
