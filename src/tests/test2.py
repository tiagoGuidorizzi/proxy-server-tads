import asyncio
import aiohttp
import time

async def burst_requests():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(10): 
            tasks.append(session.get(f"http://localhost:8000/proxy/score?q=test{i}"))
        start = time.time()
        responses = await asyncio.gather(*tasks)
        elapsed = time.time() - start
        print("Tempo total do burst:", elapsed)
        for r in responses:
            print(await r.json())

asyncio.run(burst_requests())
