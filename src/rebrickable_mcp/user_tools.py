# ===========================================
# User Tools
# ===========================================
 
from mcp.server.fastmcp import FastMCP
from src.rebrickable_mcp.config import REBRICKABLE_USER_TOKEN
from src.rebrickable_mcp.api import call_api

mcp = FastMCP("Rebrickable MCP Server")
user_token = REBRICKABLE_USER_TOKEN

def register_tools(mcp):

    # ===========================================
    # Part Lists
    # ===========================================

    @mcp.tool()
    def get_part_lists(page: int | None = None, page_size: int | None = None) -> dict | list:
        """Get a list of all the user's Part Lists."""
        params = {k: v for k, v in locals().items() if v is not None}
        return call_api(f"/users/{user_token}/partlists/", params=params)

    @mcp.tool()
    def get_parts_from_list_id(
        list_id: str,
        page: int | None = None,
        page_size: int | None = None,
        ordering: str | None = None
    ) -> dict | list:
        """Get a list of all the Parts in a specific Part List."""
        params = {k: v for k, v in locals().items() if v is not None and k != 'list_id'}
        return call_api(f"/users/{user_token}/partlists/{list_id}/parts/", params=params)

    @mcp.tool()
    def create_part_list(
        name: str,
        num_parts: int | None = None,
        is_buildable: bool | None = None
    ) -> dict | list:
        """Add a new part list."""
        data = {k: v for k, v in locals().items() if v is not None}
        return call_api(f"/users/{user_token}/partlists/", data=data, method="POST")

    @mcp.tool()
    def add_part_to_list(
        list_id: str,
        part_num: str,
        color_id: int,
        quantity: int = 1
    ) -> dict | list:
        """Add a part to a part list. If part+color already exists, updates quantity."""
        data = {"part_num": part_num, "color_id": color_id, "quantity": quantity}
        return call_api(f"/users/{user_token}/partlists/{list_id}/parts/", data=data, method="POST")

    @mcp.tool()
    def update_part_in_list(
        list_id: str,
        part_num: str,
        color_id: int,
        quantity: int
    ) -> dict | list:
        """Replace an existing Part's quantity in the Part List."""
        data = {"quantity": quantity}
        return call_api(
            f"/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/",
            data=data,
            method="PUT"
        )

    @mcp.tool()
    def delete_part_from_list(
        list_id: str,
        part_num: str,
        color_id: int
    ) -> dict | list:
        """Remove a part entirely from a list."""
        return call_api(
            f"/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/",
            method="DELETE"
        )

    # LET'S NOT GIVE AI THE ABILITY TO DELETE ENTIRE LISTS AT THE MOMENT
    # @mcp.tool()
    # def delete_part_list(list_id: str) -> dict:
    #     """Delete an entire part list."""
    #     return call_api(f"/users/{user_token}/partlists/{list_id}/", method="DELETE")
        
    # ===========================================
    # Set Lists
    # ===========================================
    
