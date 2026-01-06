import logging
import os
from typing import Any, Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from . import tools

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-obsidian-http")

api_key = os.getenv("OBSIDIAN_API_KEY")
if not api_key:
    raise ValueError(f"OBSIDIAN_API_KEY environment variable required. Working directory: {os.getcwd()}")

app = FastAPI(
    title="MCP Obsidian HTTP Server",
    description="HTTP API for MCP Obsidian server to enable external communication",
    version="0.2.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tool_handlers = {}

def add_tool_handler(tool_class: tools.ToolHandler):
    global tool_handlers
    tool_handlers[tool_class.name] = tool_class

def get_tool_handler(name: str) -> tools.ToolHandler | None:
    if name not in tool_handlers:
        return None
    return tool_handlers[name]

add_tool_handler(tools.ListFilesInDirToolHandler())
add_tool_handler(tools.ListFilesInVaultToolHandler())
add_tool_handler(tools.GetFileContentsToolHandler())
add_tool_handler(tools.SearchToolHandler())
add_tool_handler(tools.PatchContentToolHandler())
add_tool_handler(tools.AppendContentToolHandler())
add_tool_handler(tools.PutContentToolHandler())
add_tool_handler(tools.DeleteFileToolHandler())
add_tool_handler(tools.ComplexSearchToolHandler())
add_tool_handler(tools.BatchGetFileContentsToolHandler())
add_tool_handler(tools.PeriodicNotesToolHandler())
add_tool_handler(tools.RecentPeriodicNotesToolHandler())
add_tool_handler(tools.RecentChangesToolHandler())


class ToolCallRequest(BaseModel):
    name: str = Field(..., description="Name of the tool to call")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Arguments for the tool")


class ToolCallResponse(BaseModel):
    success: bool
    result: Optional[list[dict[str, Any]]] = None
    error: Optional[str] = None


class ToolListResponse(BaseModel):
    tools: list[dict[str, Any]]


def verify_api_key(authorization: Optional[str] = Header(None)) -> bool:
    if not authorization:
        return False
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return False
    
    token = parts[1]
    expected_token = os.getenv("MCP_HTTP_API_KEY")
    
    if not expected_token:
        return True
    
    return token == expected_token


@app.get("/", response_model=dict)
async def root():
    return {
        "name": "MCP Obsidian HTTP Server",
        "version": "0.2.1",
        "status": "running",
        "endpoints": {
            "list_tools": "/tools",
            "call_tool": "/tools/call"
        }
    }


@app.get("/tools", response_model=ToolListResponse)
async def list_tools(authorization: Optional[str] = Header(None)):
    if not verify_api_key(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    tools_list = [
        {
            "name": th.name,
            "description": th.get_tool_description().description,
            "inputSchema": th.get_tool_description().inputSchema
        }
        for th in tool_handlers.values()
    ]
    
    return ToolListResponse(tools=tools_list)


@app.post("/tools/call", response_model=ToolCallResponse)
async def call_tool(
    request: ToolCallRequest,
    authorization: Optional[str] = Header(None)
):
    if not verify_api_key(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    tool_handler = get_tool_handler(request.name)
    if not tool_handler:
        raise HTTPException(status_code=404, detail=f"Tool not found: {request.name}")
    
    try:
        result = tool_handler.run_tool(request.arguments)
        
        result_list = []
        for item in result:
            if hasattr(item, 'model_dump'):
                result_list.append(item.model_dump())
            elif hasattr(item, 'dict'):
                result_list.append(item.dict())
            else:
                result_list.append({"type": "text", "text": str(item)})
        
        return ToolCallResponse(success=True, result=result_list)
    except Exception as e:
        logger.error(f"Error calling tool {request.name}: {str(e)}")
        return ToolCallResponse(success=False, error=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}


def run_server(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    
    logger.info(f"Starting MCP Obsidian HTTP server on {host}:{port}")
    
    api_key_configured = os.getenv("MCP_HTTP_API_KEY")
    if api_key_configured:
        logger.info("API key authentication enabled")
    else:
        logger.warning("No API key configured - server will accept all requests")
    
    uvicorn.run(app, host=host, port=port)
