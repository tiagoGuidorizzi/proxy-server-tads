import asyncio
from fastapi import FastAPI, HTTPException
from prometheus_client import start_http_server
from app.services.queue import RequestQueue, QueueItem
from app.services.circuit import CircuitBreaker
from app.services.scheduler import Scheduler
from app.observers.log_observer import LogObserver
from app.observers.metrics_observer import MetricsObserver
import uuid
import time

app = FastAPI()

# --- Setup observers
log_obs = LogObserver()
metrics_obs = MetricsObserver()

rq = RequestQueue()
rq.attach(log_obs)
rq.attach(metrics_obs)

circuit = CircuitBreaker()
circuit.attach(log_obs)
circuit.attach(metrics_obs)

# --- Start Prometheus metrics server
start_http_server(8001)

# --- Start scheduler
scheduler = Scheduler(rate_limit_per_sec=1, use_cache=True)
asyncio.create_task(scheduler.run())

@app.get("/health")
async def health():
    return {"status":"ok","queue_size":len(rq),"circuit":circuit.state}

@app.get("/metrics")
async def metrics():
    return {"message":"Metrics server running at port 8001"}

@app.get("/proxy/score")
async def proxy_score(q: str, priority: int = 50, ttl: int = 30):
    import asyncio
    fut = asyncio.get_event_loop().create_future()
    item = QueueItem(priority=priority, created_at=time.time(), deadline=time.time()+ttl,
                     id=str(uuid.uuid4()), params={"q":q}, future=fut)
    await rq.put(item)
    try:
        result = await asyncio.wait_for(fut, timeout=10)
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout waiting upstream")
