from mcp.server.fastmcp import FastMCP
from src.rebrickable_mcp.config import REBRICKABLE_USER_TOKEN
from src.rebrickable_mcp.api import call_api

mcp = FastMCP("Rebrickable MCP Server")
user_token = REBRICKABLE_USER_TOKEN

# ===========================================
# User Tools
# ===========================================

def register_tools(mcp):

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