import streamlit as st
import json
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from tools.tool import unified_endpoint_connector

# Load environment variables
load_dotenv()

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
    # Read the JSON file
    data = json.load(uploaded_file)
    st.success("JSON file successfully loaded!")

    # Initialize LLM
    if groq_api_key:
        llm = ChatGroq(
            model="llama3-groq-8b-8192-tool-use-preview",
            temperature=0.0,
            api_key=groq_api_key
        )

        # Define agents
        openapi_analyst_agent = Agent(
            role="OpenAPI Specification Analyst",
            goal="Analyze and interpret OpenAPI specifications data to create a comprehensive understanding of the API structure",
            backstory="You are a seasoned API architect with 20 years of experience in designing and documenting APIs.",
            verbose=True,
            llm=llm,
            allow_delegation=False
        )

        user_request_interpreter_agent = Agent(
            role="User Request Interpreter, API Matcher",
            goal="Interpret user request, identify the method, parameters, and match them to appropriate API endpoints based on the OpenAPI specification.",
            backstory="With a background in both natural language processing and API integration, you excel at translating user requests into structured data.",
            verbose=True,
            llm=llm,
            allow_delegation=False
        )

        api_call_agent = Agent(
            role="API Integration Specialist",
            goal="To efficiently and accurately interact with various API endpoints and handle errors gracefully.",
            backstory="As a seasoned API Integration Specialist, I have extensive experience in working with diverse APIs across multiple domains.",
            tools=[unified_endpoint_connector],
            verbose=True,
            llm=llm,
            allow_delegation=False
        )

        # Define tasks
        analyze_openapi_task = Task(
            description="Thoroughly analyze the provided OpenAPI JSON data.",
            expected_output="A comprehensive breakdown of the API structure, including endpoints, methods, parameters, and response structures.",
            agent=openapi_analyst_agent
        )

        interpret_user_request_task = Task(
            description="Interpret user request and determine which API endpoint(s) would be most appropriate to fulfill their needs.",
            expected_output="A clear interpretation of the user's intention, identified API endpoint(s), and required parameters or request body data.",
            agent=user_request_interpreter_agent
        )

        api_call_task = Task(
            description="Analyze the output of previous Agents and Tasks, create a dynamic URL based on params and appropriate endpoint, then make a call to API.",
            expected_output="The result of the API call, including success message or error details if applicable.",
            agent=api_call_agent
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
                result = crew.kickoff(inputs={"data": data, "request": user_request, "base_url": base_url})
                st.json(result)
    else:
        st.warning("Please enter your GROQ API key in the sidebar.")
else:
    st.info("Please upload a JSON file to begin.")