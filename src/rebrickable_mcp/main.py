# ------------------------------------------------------------
# Rebrickable MCP Server
# ------------------------------------------------------------

from mcp.server.fastmcp import FastMCP
from rebrickable_mcp.config import REBRICKABLE_API_KEY, REBRICKABLE_USER_TOKEN, BASE_URL
from rebrickable_mcp.api import call_api

mcp = FastMCP("Rebrickable MCP Server")

@mcp.tool
def get_part(part_num: str) -> dict:   
    """Fetch part details from Rebrickable API, including variants."""
    return call_api(f"/lego/parts/{part_num}/")

if __name__ == "__main__":
    mcp.run()  