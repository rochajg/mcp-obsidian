from . import server
from . import http_server
import asyncio
import os

def main():
    """Main entry point for the package."""
    asyncio.run(server.main())

def main_http():
    """Main entry point for HTTP server."""
    host = os.getenv("MCP_HTTP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_HTTP_PORT", "8000"))
    http_server.run_server(host=host, port=port)

__all__ = ['main', 'main_http', 'server', 'http_server']