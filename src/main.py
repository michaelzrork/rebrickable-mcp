# ------------------------------------------------------------
# Rebrickable MCP Server
# ------------------------------------------------------------

import os
import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
from src.rebrickable_mcp import lego_tools, user_tools

mcp = FastMCP("Rebrickable MCP Server")

# ===========================================
# Register Tools
# ===========================================

user_tools.register_tools(mcp)
lego_tools.register_tools(mcp)

# ===========================================
# Server Setup
# ===========================================

def main():
    # HTTP/SSE mode for cloud deployment
    port = int(os.environ.get("PORT", 8000))
    sse = SseServerTransport("/messages/")
    
    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await mcp._mcp_server.run(
                streams[0], streams[1],
                mcp._mcp_server.create_initialization_options()
            )
        return Response()
    
    async def health_check(request):
        return Response("OK", status_code=200)
    
    app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages", app=sse.handle_post_message),
            Route("/health", endpoint=health_check, methods=["GET"]),
        ]
    )
    
    print(f"Starting TickTick MCP server on port {port}")
    print(f"Health check available at: /health")
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()