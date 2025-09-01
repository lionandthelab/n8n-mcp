#!/usr/bin/env python3
import asyncio
import json
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field
from fastmcp import FastMCP, schema
from .n8n_client import N8nClient

class CreateWorkflowParams(BaseModel):
    name: str
    nodes: List[Dict[str, Any]]
    connections: Dict[str, Any] = {}
    settings: Dict[str, Any] = {}
    tags: List[str] = []
    activate: Optional[bool] = False

class GetWorkflowParams(BaseModel):
    id: Union[str, int]

class SetActivationParams(BaseModel):
    id: Union[str, int]
    active: bool

class UpdateWorkflowParams(BaseModel):
    id: Union[str, int]
    name: Optional[str] = None
    nodes: Optional[List[Dict[str, Any]]] = None
    connections: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class DeleteWorkflowParams(BaseModel):
    id: Union[str, int]

server = FastMCP("n8n-mcp-python")
client = N8nClient()

def _as_text(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)

@server.tool(name="create_workflow", schema=schema(CreateWorkflowParams))
async def create_workflow(params: CreateWorkflowParams):
    body = {
        "name": params.name,
        "nodes": params.nodes,
        "connections": params.connections or {},
        "settings": params.settings or {},
        "tags": params.tags or [],
    }
    created = await client.create_workflow(body)
    if params.activate:
        await client.set_activation(created.get("id"), True)
        created["active"] = True
    return _as_text(created)

@server.tool(name="get_workflow", schema=schema(GetWorkflowParams))
async def get_workflow(params: GetWorkflowParams):
    wf = await client.get_workflow(params.id)
    return _as_text(wf)

@server.tool(name="list_workflows")
async def list_workflows():
    wfs = await client.list_workflows()
    return _as_text(wfs)

@server.tool(name="set_activation", schema=schema(SetActivationParams))
async def set_activation(params: SetActivationParams):
    out = await client.set_activation(params.id, params.active)
    return _as_text(out)

@server.tool(name="update_workflow", schema=schema(UpdateWorkflowParams))
async def update_workflow(params: UpdateWorkflowParams):
    original = await client.get_workflow(params.id)
    body = {
        "name": params.name if params.name is not None else original.get("name"),
        "nodes": params.nodes if params.nodes is not None else original.get("nodes", []),
        "connections": params.connections if params.connections is not None else original.get("connections", {}),
        "settings": params.settings if params.settings is not None else original.get("settings", {}),
        "tags": params.tags if params.tags is not None else original.get("tags", []),
    }
    updated = await client.update_workflow(params.id, body)
    return _as_text(updated)

@server.tool(name="delete_workflow", schema=schema(DeleteWorkflowParams))
async def delete_workflow(params: DeleteWorkflowParams):
    out = await client.delete_workflow(params.id)
    return _as_text(out)

if __name__ == "__main__":
    server.run()
