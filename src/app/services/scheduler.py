import asyncio
import time
from patterns.singleton import RequestQueue, QueueItem, QueueFullError
from services.circuit import CircuitBreaker
from patterns.command import Command
from patterns.decorator import CacheDecorator

class Scheduler:
    
    def __init__(self, rate_limit_per_sec: int = 1, use_cache: bool = True):
        self.queue = RequestQueue()
        self.circuit = CircuitBreaker()
        self.rate_limit = rate_limit_per_sec
        self.last_exec_time = 0
        self.use_cache = use_cache
        self.cache = CacheDecorator() if use_cache else None

    async def run(self):
        """Loop principal do scheduler."""
        while True:
            # obtém tamanho da fila de forma assíncrona
            queue_size = await self.queue.size()
            if queue_size == 0:
                await asyncio.sleep(0.1)
                continue

            # respeita rate limit
            now = time.time()
            elapsed = now - self.last_exec_time
            if elapsed < 1 / self.rate_limit:
                await asyncio.sleep(1 / self.rate_limit - elapsed)

            # pega o próximo item
            try:
                item = await self.queue.get()
            except asyncio.QueueEmpty:
                continue

            # verifica deadline
            if item.deadline and time.time() > item.deadline:
                self.queue.notify({"event": "dropped", "reason": "ttl_expired", "item": item})
                item.future.set_result({"status": "DROPPED", "reason": "ttl_expired"})
                continue

            # verifica circuito aberto
            if not self.circuit.allow_request():
                self.queue.notify({"event": "dropped", "reason": "circuit_open", "item": item})
                item.future.set_result({"status": "CIRCUIT_OPEN"})
                await asyncio.sleep(1 / self.rate_limit)
                continue

            # executa comando
            await self._execute(item)
            self.last_exec_time = time.time()

    async def _execute(self, item: QueueItem):
        command: Command = item.params.get("command")
        try:
            if self.use_cache and self.cache.has(command):
                result = self.cache.get(command)
            else:
                # executa comando via circuito
                result = await self.circuit.call(command.execute)
                if self.use_cache:
                    self.cache.set(command, result)

            item.future.set_result(result)
            self.queue.notify({"event": "executed", "item": item})

        except Exception as e:
            item.future.set_result({"status": "ERROR", "error": str(e)})
            self.queue.notify({"event": "error", "error": str(e), "item": item})
