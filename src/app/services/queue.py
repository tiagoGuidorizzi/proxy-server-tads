# queue.py
import asyncio
import heapq
from dataclasses import dataclass, field
from typing import Any, Optional, Dict
from app.patterns.observer import Observable

@dataclass(order=True)
class QueueItem:
    priority: int
    created_at: float = field(compare=False)
    deadline: Optional[float] = field(compare=False)
    id: str = field(compare=False)
    params: Dict[str, Any] = field(compare=False)
    future: asyncio.Future = field(compare=False)

class QueueFullError(Exception):
    pass

class RequestQueue(Observable):
    def __init__(self, max_size=200):
        super().__init__()
        self._heap = []
        self._lock = asyncio.Lock()
        self._max_size = max_size

    async def put(self, item: QueueItem):
        async with self._lock:
            if len(self._heap) >= self._max_size:
                self.notify({"event": "dropped", "item": item})
                raise QueueFullError()
            heapq.heappush(self._heap, item)
            self.notify({"event": "enqueued", "item": item})

    async def get(self) -> QueueItem:
        async with self._lock:
            if not self._heap:
                raise asyncio.QueueEmpty()
            item = heapq.heappop(self._heap)
            self.notify({"event": "dequeued", "item": item})
            return item

    async def size(self) -> int:
        async with self._lock:
            return len(self._heap)
