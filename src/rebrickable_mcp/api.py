import httpx
from src.rebrickable_mcp.config import REBRICKABLE_API_KEY, BASE_URL

def get_rebrickable_headers():
    """Generate headers for Rebrickable API requests."""
    return {
        "Authorization": f"key {REBRICKABLE_API_KEY}",
        "Content-Type": "application/json",
    }

def call_api(endpoint: str, params: dict | None = None) -> dict | list:
    """Make a GET request to the Rebrickable API."""
    url = f"{BASE_URL}{endpoint}"
    headers = get_rebrickable_headers()
    
    with httpx.Client(headers=headers) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()