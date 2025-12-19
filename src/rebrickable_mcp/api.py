import httpx
from src.rebrickable_mcp.config import REBRICKABLE_API_KEY, BASE_URL

def get_rebrickable_headers():
    """Generate headers for Rebrickable API requests."""
    return {
        "Authorization": f"key {REBRICKABLE_API_KEY}",
        "Content-Type": "application/json",
    }

def call_api(
    endpoint: str,
    params: dict | None = None,
    data: dict | None = None,
    method: str = "GET"
) -> dict | list:
    """Make a request to the Rebrickable API.
    
    Args:
        endpoint: API endpoint path
        params: Query string parameters (for GET requests)
        data: Request body as JSON (for POST/PUT requests)
        method: HTTP method (GET, POST, PUT, DELETE)
    """
    url = f"{BASE_URL}{endpoint}"
    headers = get_rebrickable_headers()
    
    with httpx.Client(headers=headers) as client:
        if method == "GET":
            response = client.get(url, params=params)
        elif method == "POST":
            response = client.post(url, json=data)
        elif method == "PUT":
            response = client.put(url, json=data)
        elif method == "DELETE":
            response = client.delete(url)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json() if response.content else {"status": "success"}
