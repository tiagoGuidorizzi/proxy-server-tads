import asyncio
import aiohttp
import time

PROXY_URL = "http://localhost:8000/proxy/score"

NUM_REQUESTS = 10  # Quantidade de requisições no burst

async def make_request(session, cpf_value):
    async with session.get(PROXY_URL, params={"cpf": cpf_value}) as resp:
        try:
            data = await resp.json()
        except Exception as e:
            data = {"error": str(e)}
        return {"cpf": cpf_value, "status": resp.status, "body": data}

async def burst_requests():
    async with aiohttp.ClientSession() as session:
        tasks = [make_request(session, f"123491203{i}") for i in range(NUM_REQUESTS)]
        start = time.time()
        responses = await asyncio.gather(*tasks)
        elapsed = time.time() - start
        print("Tempo total do burst:", elapsed)
        for r in responses:
            print(r)

if __name__ == "__main__":
    asyncio.run(burst_requests())
