# ===========================================
# User Tools
# ===========================================
 
from mcp.server.fastmcp import FastMCP
from src.rebrickable_mcp.config import REBRICKABLE_USER_TOKEN
from src.rebrickable_mcp.api import call_api
import httpx
import time

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
        
        POSTs a JSON list to add all parts in a single API call.
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
        """Internal helper for add/update logic - used by move_parts_between_lists.
        
        Includes 1-second delays between API calls to respect Rebrickable's rate limit.
        """
        try:
            existing = call_api(f"/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/")
            time.sleep(1)  # Rate limit: 1 call/second
            old_qty = existing["quantity"]
            new_qty = old_qty + quantity
            
            if new_qty <= 0:
                call_api(
                    f"/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/",
                    method="DELETE"
                )
                time.sleep(1)  # Rate limit: 1 call/second
                return {"status": "deleted", "part_num": part_num, "color_id": color_id, "old_quantity": old_qty, "removed": old_qty}
            
            call_api(
                f"/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/",
                data={"quantity": new_qty},
                method="PUT"
            )
            time.sleep(1)  # Rate limit: 1 call/second
            return {"status": "updated", "part_num": part_num, "color_id": color_id, "old_quantity": old_qty, "added": quantity, "new_quantity": new_qty}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                time.sleep(1)  # Rate limit: 1 call/second (even for 404)
                if quantity <= 0:
                    return {"status": "no_change", "part_num": part_num, "color_id": color_id, "message": "Part not in list and quantity is not positive"}
                call_api(
                    f"/users/{user_token}/partlists/{list_id}/parts/",
                    data={"part_num": part_num, "color_id": color_id, "quantity": quantity},
                    method="POST"
                )
                time.sleep(1)  # Rate limit: 1 call/second
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
        
        Optimized to minimize API calls:
        1. Fetches destination list once to check existing parts
        2. Bulk-adds new parts in single call
        3. Updates existing parts individually (with rate limiting)
        4. If emptying source completely, deletes and recreates list (2 calls vs N deletes)
        """
        results = []
        
        # Step 1: Get all parts currently in destination (1 API call)
        dest_parts = {}
        try:
            dest_response = call_api(f"/users/{user_token}/partlists/{dest_list_id}/parts/", params={"page_size": 1000})
            time.sleep(1)
            for item in dest_response.get("results", []):
                key = (item["part"]["part_num"], item["color"]["id"])
                dest_parts[key] = item["quantity"]
        except Exception:
            pass  # If fetch fails, treat all as new
        
        # Step 2: Separate into new parts vs existing parts
        new_parts = []
        existing_parts = []
        for part in parts:
            key = (part["part_num"], part["color_id"])
            if key in dest_parts:
                existing_parts.append({
                    **part,
                    "old_quantity": dest_parts[key],
                    "new_quantity": dest_parts[key] + part["quantity"]
                })
            else:
                new_parts.append(part)
        
        # Step 3: Bulk-add new parts (1 API call)
        if new_parts:
            try:
                call_api(
                    f"/users/{user_token}/partlists/{dest_list_id}/parts/",
                    data=new_parts,
                    method="POST"
                )
                time.sleep(1)
                for part in new_parts:
                    results.append({
                        "part_num": part["part_num"],
                        "color_id": part["color_id"],
                        "quantity_moved": part["quantity"],
                        "destination": {"status": "added", "part_num": part["part_num"], "color_id": part["color_id"], "quantity": part["quantity"]},
                        "source": {"status": "deleted"}
                    })
            except Exception as e:
                # If bulk add fails, fall back to individual adds
                for part in new_parts:
                    try:
                        call_api(
                            f"/users/{user_token}/partlists/{dest_list_id}/parts/",
                            data={"part_num": part["part_num"], "color_id": part["color_id"], "quantity": part["quantity"]},
                            method="POST"
                        )
                        time.sleep(1)
                        results.append({
                            "part_num": part["part_num"],
                            "color_id": part["color_id"],
                            "quantity_moved": part["quantity"],
                            "destination": {"status": "added", "part_num": part["part_num"], "color_id": part["color_id"], "quantity": part["quantity"]},
                            "source": {"status": "deleted"}
                        })
                    except Exception:
                        results.append({
                            "part_num": part["part_num"],
                            "color_id": part["color_id"],
                            "quantity_moved": 0,
                            "destination": {"status": "error", "message": str(e)},
                            "source": None
                        })
        
        # Step 4: Update existing parts individually (with rate limiting)
        for part in existing_parts:
            try:
                call_api(
                    f"/users/{user_token}/partlists/{dest_list_id}/parts/{part['part_num']}/{part['color_id']}/",
                    data={"quantity": part["new_quantity"]},
                    method="PUT"
                )
                time.sleep(1)
                results.append({
                    "part_num": part["part_num"],
                    "color_id": part["color_id"],
                    "quantity_moved": part["quantity"],
                    "destination": {
                        "status": "updated",
                        "part_num": part["part_num"],
                        "color_id": part["color_id"],
                        "old_quantity": part["old_quantity"],
                        "added": part["quantity"],
                        "new_quantity": part["new_quantity"]
                    },
                    "source": {"status": "deleted"}
                })
            except Exception as e:
                results.append({
                    "part_num": part["part_num"],
                    "color_id": part["color_id"],
                    "quantity_moved": 0,
                    "destination": {"status": "error", "message": str(e)},
                    "source": None
                })
        
        # Step 5: Check if we're emptying source completely - if so, delete and recreate (2 calls vs N deletes)
        try:
            source_response = call_api(f"/users/{user_token}/partlists/{source_list_id}/")
            time.sleep(1)
            source_name = source_response.get("name", "Unnamed List")
            source_part_count = source_response.get("num_parts", 0)
            
            # Count total parts being moved
            total_moving = sum(p["quantity"] for p in parts)
            
            if source_part_count <= total_moving:
                # Emptying completely - delete and recreate
                call_api(f"/users/{user_token}/partlists/{source_list_id}/", method="DELETE")
                time.sleep(1)
                # Recreate with same name - NOTE: This will have a NEW list_id!
                new_list = call_api(
                    f"/users/{user_token}/partlists/",
                    data={"name": source_name},
                    method="POST"
                )
                time.sleep(1)
                return {
                    "status": "moved",
                    "parts_count": len(parts),
                    "add_result": results,
                    "source_list_recreated": True,
                    "new_source_list_id": new_list.get("id"),
                    "note": f"Source list '{source_name}' was deleted and recreated with new ID: {new_list.get('id')}"
                }
            else:
                # Partial move - delete parts individually
                for part in parts:
                    try:
                        call_api(
                            f"/users/{user_token}/partlists/{source_list_id}/parts/{part['part_num']}/{part['color_id']}/",
                            method="DELETE"
                        )
                        time.sleep(1)
                    except Exception:
                        pass  # Already marked in results
        except Exception as e:
            # Fallback to individual deletes
            for part in parts:
                try:
                    call_api(
                        f"/users/{user_token}/partlists/{source_list_id}/parts/{part['part_num']}/{part['color_id']}/",
                        method="DELETE"
                    )
                    time.sleep(1)
                except Exception:
                    pass
        
        return {"status": "moved", "parts_count": len(parts), "add_result": results}

    # LET'S NOT GIVE AI THE ABILITY TO DELETE ENTIRE LISTS AT THE MOMENT
    # @mcp.tool()
    # def delete_part_list(list_id: str) -> dict:
    #     """Delete an entire part list."""
    #     return call_api(f"/users/{user_token}/partlists/{list_id}/", method="DELETE")
        
    # ===========================================
    # Set Lists
    # ===========================================
    
