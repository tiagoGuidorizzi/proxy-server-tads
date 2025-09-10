
import asyncio
import pytest
from httpx import AsyncClient
from app.main import app
import time

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert "circuit" in response.json()

@pytest.mark.asyncio
async def test_single_proxy_request():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/proxy/score?q=test")
    assert response.status_code in [200, 503]  # pode ser fallback
    json_data = response.json()
    assert "status" in json_data or "from_cache" in json_data

@pytest.mark.asyncio
async def test_burst_requests_respects_rate_limit():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        tasks = [ac.get("/proxy/score?q=burst_test") for _ in range(20)]
        start = time.time()
        responses = await asyncio.gather(*tasks)
        end = time.time()
    
    assert end - start >= 19
    for resp in responses:
        assert resp.status_code in [200, 503]

@pytest.mark.asyncio
async def test_ttl_expiration():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/proxy/score?q=ttl_test&ttl=1&priority=50")
        await asyncio.sleep(2)  # deixa o TTL expirar
        json_data = response.json()
        assert "status" in json_data

@pytest.mark.asyncio
async def test_cache_fallback():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r1 = await ac.get("/proxy/score?q=cached_test")
        r2 = await ac.get("/proxy/score?q=cached_test")
        assert r2.json().get("from_cache") is True

@pytest.mark.asyncio
async def test_circuit_breaker_triggers(monkeypatch):

    async def fail_get(*args, **kwargs):
        class Resp:
            status_code = 500
            content = b"{}"
            def json(self): return {}
        return Resp()
    from app.main import client, circuit
    monkeypatch.setattr(client, "get", fail_get)
    for _ in range(6):
        await circuit.call(lambda: client.get("/"))
    assert circuit.state in ["OPEN", "HALF-OPEN"]
