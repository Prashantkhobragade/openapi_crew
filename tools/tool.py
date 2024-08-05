import requests
from crewai_tools import tool

BASE_URL = "http://localhost:8000"

@tool("unified_endpoint_connector")
def unified_endpoint_connector(method: str, endpoint: str, params: dict = None) -> dict:
    """
    Handles GET and DELETE requests to a FastAPI endpoint.

    Args:
        method (str): The HTTP method to use ('GET' or 'DELETE').
        endpoint (str): The API endpoint to target (e.g., '/items/').
        params (dict, optional): The parameters to include in the request (for GET) or specify the resource (for DELETE).

    Returns:
        dict: The response from the server, parsed into a Python dictionary.
    
    """

    # Replace placeholders in the endpoint with actual values from params
    if params:
        endpoint = endpoint.format(**params)

    url = f"{BASE_URL}{endpoint}"
    print(url)
    try:
        if method.lower() == "get":
            response = requests.get(url, params=params)
        elif method.lower() == "delete":
            response = requests.delete(url, params=params)
        else:
            return {"error": "Invalid method. Use 'GET' or 'DELETE'."}
        
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return {"error": "Client Error"}
        else:
            return {"error": str(e)}
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


#result = unified_endpoint_connector(method="GET", endpoint="/items/{item_number}",params={"item_number": 90})
#print(result)