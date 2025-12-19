from mcp.server.fastmcp import FastMCP
from src.rebrickable_mcp.config import REBRICKABLE_USER_TOKEN
from src.rebrickable_mcp.api import call_api

mcp = FastMCP("Rebrickable MCP Server")
user_token = REBRICKABLE_USER_TOKEN

# ===========================================
# LEGO Tools
# ===========================================

def register_tools(mcp):

    @mcp.tool()
    def get_part(part_num: str) -> dict | list:   
        """Fetch part details from Rebrickable API, including variants."""
        return call_api(f"/lego/parts/{part_num}/", params={})