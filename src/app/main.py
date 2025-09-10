import asyncio
import time
import uuid
from fastapi import FastAPI, HTTPException, Query
from app.services.queue import RequestQueue, QueueItem, QueueFullError
from app.patterns.command import Command

QUEUE_MAX_SIZE = 200
REQUEST_TTL = 30

app = FastAPI()
rq = RequestQueue(max_size=QUEUE_MAX_SIZE)

@app.get("/health")
async def health():
    """Health check simples."""
    return {"status": "ok", "queue_size": await rq.size()}

@app.get("/proxy/score")
async def proxy_score(cpf: str = Query(...)):
    """
    Proxy para o upstream score.hsborges.dev
    - cpf: obrigatório
    """
    fut = asyncio.get_event_loop().create_future()
    item = QueueItem(
        priority=50,
        created_at=time.time(),
        deadline=time.time() + REQUEST_TTL,
        id=str(uuid.uuid4()),
        params={"cpf": cpf},
        future=fut
    )
    try:
        await rq.put(item)
    except QueueFullError:
        raise HTTPException(status_code=503, detail="Queue full, request dropped")

    try:
        result = await asyncio.wait_for(fut, timeout=REQUEST_TTL + 5)
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout waiting upstream")

async def scheduler_worker():
    while True:
        try:
            item = await rq.get()
        except asyncio.QueueEmpty:
            await asyncio.sleep(0.1)
            continue

        if item.deadline and time.time() > item.deadline:
            item.future.set_result({"status": "DROPPED", "reason": "ttl_expired"})
            continue

        cpf = item.params.get("cpf")
        command = Command(cpf=cpf)
        result = await command.execute()
        item.future.set_result(result)
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup():
    asyncio.create_task(scheduler_worker())
