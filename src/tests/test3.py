import asyncio
import aiohttp
import time

PROXY_URL = "http://localhost:8000/proxy/score"

NUM_REQUESTS = 30        
BURST_INTERVAL = 0.05    

async def make_request(session, q_value):
    start = time.time()
    try:
        async with session.get(PROXY_URL, params={"q": q_value}) as resp:
            elapsed = time.time() - start
            data = await resp.json()
            status = data.get("status", "unknown")
            from_cache = data.get("from_cache", False)
            return {
                "q": q_value,
                "status": status,
                "from_cache": from_cache,
                "latency": elapsed,
                "raw": data
            }
    except Exception as e:
        return {"q": q_value, "status": "error", "error": str(e), "latency": time.time()-start}

async def run_burst():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(NUM_REQUESTS):
            q_value = f"test{i % 10}"  # Alguns valores repetidos para testar cache
            tasks.append(make_request(session, q_value))
            await asyncio.sleep(BURST_INTERVAL)  # Simula rajada de requisições rápidas

        results = await asyncio.gather(*tasks)
        return results

def summarize_results(results):
    total = len(results)
    cache_hits = sum(1 for r in results if r.get("from_cache"))
    errors = sum(1 for r in results if r.get("status") == "error")
    dropped = sum(1 for r in results if r.get("status") == "DROPPED")
    print(f"Total requests: {total}")
    print(f"Cache hits: {cache_hits}")
    print(f"Dropped requests: {dropped}")
    print(f"Errors: {errors}")
    print("\nSample responses:")
    for r in results[:5]:
        print(r)

if __name__ == "__main__":
    results = asyncio.run(run_burst())
    summarize_results(results)
