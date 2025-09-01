import os
import json
from typing import Any, Dict, List, Optional, Union

import httpx

class N8nClient:
    def __init__(self, base: Optional[str] = None, api_key: Optional[str] = None, timeout: int = 30):
        self.base = (base or os.getenv("N8N_BASE") or "http://localhost:5678").rstrip("/")
        self.api_key = api_key or os.getenv("N8N_API_KEY") or ""
        self.timeout = timeout
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-N8N-API-KEY": self.api_key,
        }

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base}/api/v1{path}"

    async def _request(self, method: str, path: str, json_body: Optional[Dict[str, Any]] = None):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.request(
                method=method,
                url=self._url(path),
                headers=self.headers,
                json=json_body
            )
            if resp.status_code >= 400:
                raise RuntimeError(f"n8n API {resp.status_code}: {resp.text}")
            if resp.text.strip() == "":
                return None
            return resp.json()

    async def create_workflow(self, body: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "/workflows", body)

    async def get_workflow(self, workflow_id: Union[str, int]) -> Dict[str, Any]:
        return await self._request("GET", f"/workflows/{workflow_id}")

    async def list_workflows(self) -> List[Dict[str, Any]]:
        return await self._request("GET", "/workflows")

    async def update_workflow(self, workflow_id: Union[str, int], body: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("PATCH", f"/workflows/{workflow_id}", body)

    async def delete_workflow(self, workflow_id: Union[str, int]) -> Dict[str, Any]:
        out = await self._request("DELETE", f"/workflows/{workflow_id}")
        return out or {"deleted": True, "id": str(workflow_id)}

    async def set_activation(self, workflow_id: Union[str, int], active: bool) -> Dict[str, Any]:
        path = f"/workflows/{workflow_id}/activate" if active else f"/workflows/{workflow_id}/deactivate"
        return await self._request("POST", path)
