# ===========================================
# LEGO Tools
# ===========================================

from mcp.server.fastmcp import FastMCP
from src.rebrickable_mcp.config import REBRICKABLE_USER_TOKEN
from src.rebrickable_mcp.api import call_api
from src.rebrickable_mcp.cache import COLORS

mcp = FastMCP("Rebrickable MCP Server")
user_token = REBRICKABLE_USER_TOKEN

def register_tools(mcp):

    # ===========================================
    # Color Tools
    # ===========================================

    @mcp.tool()
    def list_colors() -> list[dict]:
        """Get all Rebrickable color names and IDs for quick reference."""
        return [
            {"id": cid, "name": data["name"]}
            for cid, data in sorted(COLORS.items(), key=lambda x: x[1]["name"])
        ]
    

    # ===========================================
    # Part Tools
    # ===========================================
    
    @mcp.tool()
    def get_part(part_num: str) -> dict | list:   
        """Fetch part details from Rebrickable API, including variants."""
        return call_api(f"/lego/parts/{part_num}/")

    @mcp.tool()
    def search_parts(
        search: str,
        part_cat_id: int | None = None,
        page: int | None = None,
        page_size: int | None = None
    ) -> dict | list:
        """Search for parts by name or number."""
        params = {k: v for k, v in locals().items() if v is not None}
        return call_api("/lego/parts/", params=params)

    @mcp.tool()
    def get_part_colors(part_num: str) -> dict | list:
        """Get all colors a specific part comes in."""
        return call_api(f"/lego/parts/{part_num}/colors/")
