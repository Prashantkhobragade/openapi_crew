from crewai import Task
from src.agent import openapi_analyst_agent, user_request_interpreter_agent, api_call_agent



def analyze_openapi_task():
    return  Task(
                    description="Thoroughly analyze the provided OpenAPI JSON data. Understand all endpoints, their purposes, parameters, request bodies, and response structures. Create a detailed mental model of the API's capabilities, limitations, and overall structure.",
                    expected_output="""A comprehensive breakdown of the API structure, including:
                                                1. List of all available endpoints with their HTTP methods
                                                2. Purpose of each endpoint
                                                3. Required and optional parameters for each endpoint
                                                4. Request body structures where applicable
                                                5. Response structures and status codes
                                        """,
                    agent = openapi_analyst_agent
                )
    
def interpret_user_request_task():
    return Task(
                    description="Listen to user request {request} Identify the Method, params and determine which API endpoint(s) would be most appropriate to fulfill their needs. Translate natural language requests into specific API calls, taking into account the API structure provided by the OpenAPI Analyst.",
                    expected_output="""For each user request:
                                            1. A clear interpretation of the user's intention
                                            2. Identification of the Method(GET, POST, DELETE) to fulfill the request. 
                                            3. Identification of the most appropriate API endpoint(s) to fulfill the request
                                            4. Any required parameters or request body data needed for the API call
                                            5. A JSON output which contains information extracted from above Foure points.
                                        """,
                    agent = user_request_interpreter_agent
                )
    
def api_call_task():
    return Task(
                    description = """analyze the output of previous Agents and Tasks, create a dynamic url based on params and appropriate endpoint. 
                                        Then, make a call to API. 
                                        Ensure that errors are handled gracefully and return clear messages like if url is not found then return error: 404""",
                    expected_output="If the operation is successful, return a success message along with a JSON output containing only the request result. Otherwise, return an error message",
                    agent = api_call_agent
                )
