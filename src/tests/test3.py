import asyncio
import aiohttp
import time

PROXY_URL = "http://localhost:8000/proxy/score"

NUM_REQUESTS = 30        
BURST_INTERVAL = 0.05    

# Lista de CPFs fictícios para teste
TEST_CPFS = [
    "11111111111", "22222222222", "33333333333", 
    "44444444444", "55555555555", "66666666666",
    "77777777777", "88888888888", "99999999999",
    "00000000000"
]

async def make_request(session, cpf):
    start = time.time()
    try:
        async with session.get(PROXY_URL, params={"cpf": cpf}) as resp:
            elapsed = time.time() - start
            try:
                data = await resp.json()
            except Exception:
                data = await resp.text()
            return {
                "cpf": cpf,
                "status_code": resp.status,
                "latency": elapsed,
                "response": data
            }
    except Exception as e:
        return {
            "cpf": cpf,
            "status": "error",
            "error": str(e),
            "latency": time.time() - start
        }

async def run_burst():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(NUM_REQUESTS):
            cpf = TEST_CPFS[i % len(TEST_CPFS)] 
            tasks.append(make_request(session, cpf))
            await asyncio.sleep(BURST_INTERVAL)

        results = await asyncio.gather(*tasks)
        return results

def summarize_results(results):
    total = len(results)
    errors = sum(1 for r in results if r.get("status") == "error")
    print(f"Total requests: {total}")
    print(f"Errors: {errors}")
    print("\nSample responses:")
    for r in results[:5]:
        print(r)

if __name__ == "__main__":
    results = asyncio.run(run_burst())
    summarize_results(results)

