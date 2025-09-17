import asyncio
import aiohttp
import time

PROXY_URL = "http://localhost:8000/proxy/score"

NUM_REQUESTS = 10        
BURST_INTERVAL = 0.05    

# Lista de CPFs fictícios para teste
TEST_CPFS = [
    "72582622370", "03397339693", "27397278876", 
    "75101055603", "70910722609", "31454669411",
    "99586270785", "41712508032", "27298532510",
    "05837519971"
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
    print(f"Total de requisições: {total}")
    print(f"Erros: {errors}")
    print("\nRespostas:")
    for r in results[:5]:
        print("\n- Requisição:", r.get("response", r.get("cpf")), "\n- Status:", r.get("status_code", r.get("status")), "\n- Latência: {:.2f}s".format(r["latency"]))

if __name__ == "__main__":
    results = asyncio.run(run_burst())
    summarize_results(results)

