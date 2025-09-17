import asyncio
import time
import uuid
from fastapi import FastAPI, HTTPException, Query
from app.patterns.singleton import RequestQueue, QueueItem, QueueFullError
from app.patterns.command import Command

REQUEST_TTL = 30

app = FastAPI()
rq = RequestQueue()

async def interactive_terminal():
    while True:
        cpf = input("Digite o CPF para consulta (ou 'exit' para sair): ").strip()
        if cpf.lower() == "exit":
            break
        async with asyncio.get_event_loop():
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
                print("Fila cheia, request descartada")
                continue

            try:
                result = await asyncio.wait_for(fut, timeout=REQUEST_TTL + 5)
                print("Resultado:", result)
            except asyncio.TimeoutError:
                print("Timeout aguardando upstream")

@app.get("/health")
async def health():
    """Health check simples."""
    return {"status": "ok", "queue_size": await rq.size()}

@app.get("/metrics")
async def metrics():
    """Métricas simples."""
    return {
        "queue_size": await rq.size(),
        "max_queue_size": rq.max_size
    }

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


if __name__ == "__main__":
    print("Iniciando terminal interativo. Use CTRL+C para sair.")
    asyncio.run(interactive_terminal())
