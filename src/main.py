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
from src.rebrickable_mcp.config import REBRICKABLE_USER_TOKEN, BASE_URL
from src.rebrickable_mcp.api import call_api

mcp = FastMCP("Rebrickable MCP Server")
user_token = REBRICKABLE_USER_TOKEN

@mcp.tool()
def get_part(part_num: str) -> dict | list:   
    """Fetch part details from Rebrickable API, including variants."""
    return call_api(f"/lego/parts/{part_num}/", params={})

@mcp.tool()
def get_part_lists(page: int | None = None, page_size: int | None = None) -> dict | list:
    """Get a list of all the user's Part Lists."""
    params = {k: v for k, v in {"page": page, "page_size": page_size}.items() if v is not None}
    return call_api(f"/users/{user_token}/partlists/",params)

@mcp.tool()
def get_parts_from_list_id(list_id: str, page: int | None = None, page_size: int | None = None, ordering: str | None = None):
    """Get a list of all the Parts in a specific Part List."""
    params = {k: v for k, v in {"page": page, "page_size": page_size, "ordering": ordering}.items() if v is not None}
    return call_api(f"/users/{user_token}/partlists/{list_id}/parts/")

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