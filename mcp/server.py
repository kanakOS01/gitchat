from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    name='GitChat MCP',
    host='0.0.0.0',
    port=8010,
)

