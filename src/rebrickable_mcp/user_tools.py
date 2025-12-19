# ===========================================
# User Tools
# ===========================================
 
from mcp.server.fastmcp import FastMCP
from src.rebrickable_mcp.config import REBRICKABLE_USER_TOKEN
from src.rebrickable_mcp.api import call_api
import httpx

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
        """Add a part to a part list. If part+color already exists, returns error - use add_or_update_part instead."""
        data = {"part_num": part_num, "color_id": color_id, "quantity": quantity}
        return call_api(f"/users/{user_token}/partlists/{list_id}/parts/", data=data, method="POST")

    @mcp.tool()
    def add_parts_to_list(
        list_id: str,
        parts: list[dict]
    ) -> dict | list:
        """Add multiple parts to a part list in one call.
        
        parts: List of dicts with keys: part_num, color_id, quantity
        Example: [{"part_num": "3020", "color_id": 0, "quantity": 5}, {"part_num": "3021", "color_id": 72, "quantity": 10}]
        """
        return call_api(f"/users/{user_token}/partlists/{list_id}/parts/", data=parts, method="POST")

    @mcp.tool()
    def add_or_update_part(
        list_id: str,
        part_num: str,
        color_id: int,
        quantity: int = 1
    ) -> dict:
        """Add a part to a list, or increase quantity if it already exists.
        
        If the part+color doesn't exist in the list, adds it with the given quantity.
        If it already exists, increases the quantity by the given amount.
        If the resulting quantity would be 0 or less, deletes the part from the list.
        """
        try:
            # Check if part exists in list
            existing = call_api(f"/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/")
            old_qty = existing["quantity"]
            new_qty = old_qty + quantity
            
            if new_qty <= 0:
                # Delete if quantity would be 0 or negative
                call_api(
                    f"/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/",
                    method="DELETE"
                )
                return {"status": "deleted", "part_num": part_num, "color_id": color_id, "old_quantity": old_qty, "removed": old_qty}
            
            # Update with new total
            call_api(
                f"/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/",
                data={"quantity": new_qty},
                method="PUT"
            )
            return {"status": "updated", "part_num": part_num, "color_id": color_id, "old_quantity": old_qty, "added": quantity, "new_quantity": new_qty}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Doesn't exist, add fresh (only if positive quantity)
                if quantity <= 0:
                    return {"status": "no_change", "part_num": part_num, "color_id": color_id, "message": "Part not in list and quantity is not positive"}
                call_api(
                    f"/users/{user_token}/partlists/{list_id}/parts/",
                    data={"part_num": part_num, "color_id": color_id, "quantity": quantity},
                    method="POST"
                )
                return {"status": "added", "part_num": part_num, "color_id": color_id, "quantity": quantity}
            else:
                raise
    
    @mcp.tool()
    def get_part_in_list(
        list_id: str,
        part_num: str,
        color_id: int,
        quantity: int
    ) -> dict | list:
        """Get details about a specific Part in the Part List."""
        data = {"quantity": quantity}
        return call_api(
            f"/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/",
            data=data,
            method="GET"
        )
    
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

    def _add_or_update_part_internal(list_id: str, part_num: str, color_id: int, quantity: int) -> dict:
        """Internal helper for add/update logic - used by move_parts_between_lists."""
        try:
            existing = call_api(f"/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/")
            old_qty = existing["quantity"]
            new_qty = old_qty + quantity
            
            if new_qty <= 0:
                call_api(
                    f"/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/",
                    method="DELETE"
                )
                return {"status": "deleted", "part_num": part_num, "color_id": color_id, "old_quantity": old_qty, "removed": old_qty}
            
            call_api(
                f"/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/",
                data={"quantity": new_qty},
                method="PUT"
            )
            return {"status": "updated", "part_num": part_num, "color_id": color_id, "old_quantity": old_qty, "added": quantity, "new_quantity": new_qty}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                if quantity <= 0:
                    return {"status": "no_change", "part_num": part_num, "color_id": color_id, "message": "Part not in list and quantity is not positive"}
                call_api(
                    f"/users/{user_token}/partlists/{list_id}/parts/",
                    data={"part_num": part_num, "color_id": color_id, "quantity": quantity},
                    method="POST"
                )
                return {"status": "added", "part_num": part_num, "color_id": color_id, "quantity": quantity}
            else:
                raise

    @mcp.tool()
    def move_parts_between_lists(
        source_list_id: str,
        dest_list_id: str,
        parts: list[dict]
    ) -> dict:
        """Move parts from one list to another.
        
        parts: List of dicts with keys: part_num, color_id, quantity
        Example: [{"part_num": "3020", "color_id": 0, "quantity": 5}]
        
        Adds parts to destination list, then removes from source list.
        """
        results = []
        for part in parts:
            part_num = part["part_num"]
            color_id = part["color_id"]
            quantity = part["quantity"]
            
            # Add to destination (handles existing parts)
            dest_result = _add_or_update_part_internal(dest_list_id, part_num, color_id, quantity)
            
            # Remove from source (handles partial moves)
            source_result = _add_or_update_part_internal(source_list_id, part_num, color_id, -quantity)
            
            results.append({
                "part_num": part_num,
                "color_id": color_id,
                "quantity_moved": quantity,
                "destination": dest_result,
                "source": source_result
            })
        
        return {"status": "moved", "parts_count": len(parts), "add_result": results}

    # LET'S NOT GIVE AI THE ABILITY TO DELETE ENTIRE LISTS AT THE MOMENT
    # @mcp.tool()
    # def delete_part_list(list_id: str) -> dict:
    #     """Delete an entire part list."""
    #     return call_api(f"/users/{user_token}/partlists/{list_id}/", method="DELETE")
        
    # ===========================================
    # Set Lists
    # ===========================================
    
