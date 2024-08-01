import json
from dotenv import load_dotenv
import os

from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
import requests

from tools.tool import unified_endpoint_connector

# Replace 'your_file.json' with the name of your JSON file
filename = 'openapi.json'

# Open and read the JSON file
with open(filename, 'r') as file:
    data = json.load(file)



load_dotenv()

#Groq API key
try:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise ValueError("Groq api key is not found")
except:
    print("Error: Groq API key is not found")

# llm
llm = ChatGroq(
    model = "llama3-groq-8b-8192-tool-use-preview",
    temperature = 0.0,
    api_key = GROQ_API_KEY
)

#agent

# Agent 1: OpenAPI Analyst
openapi_analyst_agent = Agent(
    role="OpenAPI Specification Analyst",
    goal="Analyze and interpret OpenAPI specifications data {data} to create a comprehensive understanding of the API structure",
    backstory="You are a seasoned API architect with 20 years of experience in designing and documenting APIs. Your expertise lies in quickly grasping complex API structures and translating technical specifications into clear, actionable insights. You've worked on hundreds of API projects across various industries, making you an unparalleled expert in API analysis.",
    verbose=True,
    llm = llm,
    allow_delegation=False
)


#Agent 2: User Request Interpreter
user_request_interpreter_agent = Agent(
    role="User Request Interpreter, API Matcher and Json output generator",
    goal="Interpret user request {request}, Identify the Method and match them to appropriate API endpoints based on the OpenAPI specification and generate Json output for API calls",
    backstory="With a background in both natural language processing and API integration, you excel at translating user requests into structured data. Your 10 years of experience in building conversational AI systems that interact with complex APIs have made you an expert in generating precise JSON outputs for various API interactions.",
    tools = [unified_endpoint_connector],
    verbose=True,
    llm=llm,
    allow_delegation=False
)



#task
analyze_openapi_task = Task(
    description="Thoroughly analyze the provided OpenAPI JSON data. Understand all endpoints, their purposes, parameters, request bodies, and response structures. Create a detailed mental model of the API's capabilities, limitations, and overall structure.",
    expected_output="""A comprehensive breakdown of the API structure, including:
    1. List of all available endpoints with their HTTP methods
    2. Purpose of each endpoint
    3. Required and optional parameters for each endpoint
    4. Request body structures where applicable
    5. Response structures and status codes""",
    agent = openapi_analyst_agent
)


interpret_user_request_task = Task(
    description="Listen to user request {request} Identify the Method and determine which API endpoint(s) would be most appropriate to fulfill their needs. Translate natural language requests into specific API calls, taking into account the API structure provided by the OpenAPI Analyst.",
    expected_output="""For each user request:
    1. A clear interpretation of the user's intention
    2. Identification of the Method(GET, POST, DELETE) to fulfill the request. 
    3. Identification of the most appropriate API endpoint(s) to fulfill the request
    4. Any required parameters or request body data needed for the API call
    5. A JSON output which contains information extracted from above Foure points.
    """,
    agent = user_request_interpreter_agent
)


interpret_and_generate_json_task = Task(
    description="Analyze JSON output given by previous task, Identify the Method and determine the appropriate API endpoint, and generate a JSON output for API call",
    expected_output="A JSON string containing API call response.",
    agent = user_request_interpreter_agent
)

#crew
crew = Crew(
    agents=[openapi_analyst_agent, user_request_interpreter_agent],
    tasks=[analyze_openapi_task, interpret_user_request_task],
    proccess = Process.sequential,
    verbose=True
)

result = crew.kickoff(inputs={"data": data,
                            "request":"get me the details of item_number 111"})
print(result)
