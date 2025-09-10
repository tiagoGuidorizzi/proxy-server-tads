import httpx
import os
from typing import Any, Dict

UPSTREAM_URL = os.getenv("UPSTREAM_URL", "https://score.hsborges.dev/api/score")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "5.0"))
CLIENT_ID = os.getenv("CLIENT_ID", "1")  # caso queira tornar configurável

class Command:
    def __init__(self, cpf: str):
        self.endpoint = UPSTREAM_URL
        self.params = {"cpf": cpf}

    async def execute(self) -> Dict[str, Any]:
        """Executa a chamada HTTP real ao upstream."""
        headers = {
            "accept": "application/json",
            "client-id": CLIENT_ID
        }
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            try:
                response = await client.get(self.endpoint, params=self.params, headers=headers)
                try:
                    data = response.json() if response.content else None
                except ValueError:
                    data = response.text
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
