import asyncio
import time
from typing import Any, Optional


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class QueueFullError(Exception):
    """Erro quando a fila está cheia."""
        


class QueueItem:
    def __init__(self, priority: int, created_at: float, deadline: Optional[float], id: str, params: dict, future: asyncio.Future):
        self.priority = priority
        self.created_at = created_at
        self.deadline = deadline
        self.id = id
        self.params = params
        self.future = future


class RequestQueue(metaclass=SingletonMeta):
    def __init__(self, max_size: int = 200):
        self.queue: list[QueueItem] = []
        self.max_size = max_size
        self._lock = asyncio.Lock()

    async def put(self, item: QueueItem):
        async with self._lock:
            if len(self.queue) >= self.max_size:
                raise QueueFullError("Queue is full")
            self.queue.append(item)

    async def get(self) -> QueueItem:
        async with self._lock:
            if not self.queue:
                raise asyncio.QueueEmpty()
            return self.queue.pop(0)

    async def size(self) -> int:
        async with self._lock:
            return len(self.queue)
