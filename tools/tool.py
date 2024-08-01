import requests
from crewai_tools import tool

BASE_URL = "http://localhost:8000"

@tool("unified_endpoint_connector")
def unified_endpoint_connector(action: str, item_number: int = None, item_name: str = None, value: int = None) -> dict:
    """
    Unified tool to connect to various endpoints (POST, GET, DELETE) based on the action parameter.

    Args:
        action (str): The action to perform ("post", "get", "delete").
        item_number (int, optional): The unique identifier for the item (required for post and delete actions).
        item_name (str, optional): The name of the item (required for post action).
        value (int, optional): The value or price of the item (required for post action).

    Returns:
        dict: The JSON response from the server, parsed into a Python dictionary.
    """
    if action == "post":
        if item_number is None or item_name is None or value is None:
            return {"error": "Missing required parameters for POST action"}
        url = f"{BASE_URL}/items/"
        data = {"item_number": item_number, "item_name": item_name, "value": value}
        response = requests.post(url, json=data)
        return response.json()
    
    elif action == "get":
        url = f"{BASE_URL}/items/"
        response = requests.get(url)
        return response.json()
    
    elif action == "delete":
        if item_number is None:
            return {"error": "Missing required item_number for DELETE action"}
        url = f"{BASE_URL}/items/{item_number}"
        response = requests.delete(url)
        
        if response.status_code == 404:
            return {"message": "Item not found"}
        elif response.status_code == 200:
            return response.json()
        else:
            return {"message": "An error occurred", "status_code": response.status_code}
    
    else:
        return {"error": "Invalid action. Use 'post', 'get', or 'delete'."}
