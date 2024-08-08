import streamlit as st
import json
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from tools.tool import unified_endpoint_connector
from azureai import AzureAI
from appconfig import AppConfig

# Load environment variables
load_dotenv()


#creating an instance for app config
config = AppConfig()

#Create an instance of AzureAI using the config
azure_ai = AzureAI(config)


# Set page title
st.set_page_config(page_title="CrewAI OpenAPI Analyzer")
st.title("🤖 CrewAI OpenAPI Analyzer")

# Sidebar for API key and base URL input
st.sidebar.header("Configuration")
groq_api_key = st.sidebar.text_input("Enter GROQ API Key", type="password")
base_url = st.sidebar.text_input("Enter Base URL or API URL")

# File uploader for JSON file
uploaded_file = st.file_uploader("Choose a JSON file", type="json")

if uploaded_file is not None:
    try:
        # Read the JSON file and ensure it's a valid JSON object
        data = json.loads(uploaded_file.getvalue())
        st.success("JSON file successfully loaded!")
    except json.JSONDecodeError:
        st.error("Invalid JSON file. Please upload a valid JSON file.")
        data = None

    # Initialize LLM
    llm = azure_ai.get_client()
    if groq_api_key:
        llm = ChatGroq(
            model="llama3-groq-8b-8192-tool-use-preview",
            temperature=0.0,
            api_key=groq_api_key
        )

        # Define agents
        openapi_analyst_agent = Agent(
            role="OpenAPI Specification Analyst",
            goal="""Analyze and interpret OpenAPI specifications data {data} to create a 
                    comprehensive understanding of the API structure""",
            backstory="""You are a seasoned API architect with 20 years of experience in designing and documenting APIs. 
                        Your expertise lies in quickly grasping complex API structures and translating technical specifications into clear, 
                        actionable insights. You've worked on hundreds of API projects across various industries, making you an unparalleled 
                        expert in API analysis.""",
            verbose=True,
            llm = llm,
            allow_delegation=False
        )

        user_request_interpreter_agent = Agent(
            role="User Request Interpreter, API Matcher",
            goal="""Interpret user request {request}, identify the method, parameters, and match them to appropriate API endpoints based on 
                    the OpenAPI specification. Ensure the agent parses the user's request accurately to identify the correct API endpoint 
                    and params.""",
            backstory="""With a background in both natural language processing and API integration, you excel at translating user requests into 
                        structured data. Your 10 years of experience in building conversational AI systems that interact with complex APIs have 
                        made you an expert in generating precise JSON outputs for various API interactions.""",
            tools = [unified_endpoint_connector],
            verbose=True,
            llm=llm,
            max_iter = 10,
            allow_delegation=False
        )

        api_call_agent = Agent(
            role = "API Integration Specialist",
            goal = """To efficiently and accurately interact with various API endpoints. and Ensure that the agent itself is 
                    handling errors gracefully and returning clear messages
                    and do not try something else once you got right answer. use this tool unified_endpoint_connector for making the api calls. """,
            backstory = """As a seasoned API Integration Specialist, I have extensive experience in working with diverse APIs across 
                        multiple domains. My expertise lies in understanding API structures, authentication methods, and data formats. 
                        I was created to bridge the gap between complex API systems and user requirements, making data access and 
                        manipulation a breeze for users of all technical levels.""",
            tools = [unified_endpoint_connector],
            verbose=True,
            llm=llm,
            max_iter = 10,
            allow_delegation=False
        )

        # Define tasks
        analyze_openapi_task = Task(
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

        interpret_user_request_task = Task(
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

        api_call_task = Task(
            description = """analyze the output of previous Agents and Tasks, create a dynamic url based on params and appropriate endpoint. 
                    Then, make a call to API. 
                    Ensure that errors are handled gracefully and return clear messages like if url is not found then return error: 404""",
            expected_output="The actual result of the API call, including success message or error details if applicable",
            agent = api_call_agent
        )

        # Create crew
        crew = Crew(
            agents=[openapi_analyst_agent, user_request_interpreter_agent, api_call_agent],
            tasks=[analyze_openapi_task, interpret_user_request_task, api_call_task],
            process=Process.sequential,
            verbose=True
        )

        # User input for request
        user_request = st.text_input("Enter your request:")

        if st.button("Process Request"):
            with st.spinner("Processing your request..."):
                try:
                    result = crew.kickoff(inputs={"data": data, "request": user_request, "base_url": base_url})
                    """
                    # Parse the result to extract the actual API response
                    try:
                        api_response = json.loads(result)
                        st.json(api_response)
                    except json.JSONDecodeError:
                        st.write("API Response:", result)
                    """
                    # Display the full CrewAI process output for debugging
                    with st.expander("View full CrewAI process output"):
                        st.write(result)
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.write("Please check your inputs and try again.")

    elif not groq_api_key:
        st.warning("Please enter your GROQ API key in the sidebar.")
else:
    st.info("Please upload a JSON file to begin.")