import httpx
import os
from typing import Any, Dict

UPSTREAM_URL = os.getenv("UPSTREAM_URL", "https://score.hsborges.dev/score")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "5.0"))

class Command:
    def __init__(self, endpoint: str = UPSTREAM_URL, params: Dict[str, Any] = None):
        self.endpoint = endpoint
        self.params = params or {}

    async def execute(self) -> Dict[str, Any]:
        """Executa a chamada HTTP real ao upstream."""
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            try:
                response = await client.get(self.endpoint, params=self.params)
                data = response.json() if response.content else None
                return {
                    "endpoint": self.endpoint,
                    "params": self.params,
                    "status_code": response.status_code,
                    "body": data
                }
            except httpx.RequestError as e:
                return {
                    "endpoint": self.endpoint,
                    "params": self.params,
                    "status": "error",
                    "error": str(e)
                }
