import json
from dotenv import load_dotenv
import os


from crewai import Agent
from langchain_groq import ChatGroq
import requests

from tools.tool import unified_endpoint_connector

#Groq API key
try:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise ValueError("Groq api key is not found")
except:
    print("Error: Groq API key is not found")

llm = ChatGroq(
            model = "llama3-groq-8b-8192-tool-use-preview",
            temperature = 0.0,
            api_key = GROQ_API_KEY
            )

        
def openapi_analyst_agent():
    return Agent(
                role="OpenAPI Specification Analyst",
                goal="Analyze and interpret OpenAPI specifications data {data} to create a comprehensive understanding of the API structure",
                backstory="You are a seasoned API architect with 20 years of experience in designing and documenting APIs. Your expertise lies in quickly grasping complex API structures and translating technical specifications into clear, actionable insights. You've worked on hundreds of API projects across various industries, making you an unparalleled expert in API analysis.",
                verbose=True,
                llm = llm,
                allow_delegation=False
            )
    
def user_request_interpreter_agent():
    return Agent(
                role="User Request Interpreter, API Matcher",
                goal="""Interpret user request {request}, identify the method, parameters, and match them to appropriate API endpoints based on 
                            the OpenAPI specification. Ensure the agent parses the user's request accurately to identify the correct API endpoint and parameters.""",
                backstory="With a background in both natural language processing and API integration, you excel at translating user requests into structured data. Your 10 years of experience in building conversational AI systems that interact with complex APIs have made you an expert in generating precise JSON outputs for various API interactions.",
                #tools = [unified_endpoint_connector],
                verbose=True,
                llm=llm,
                #max_iter = 12,
                allow_delegation=False
            )
    
def api_call_agent():
    return Agent(
                role = "API Integration Specialist",
                goal = """To efficiently and accurately interact with various API endpoints. and Ensure that the agent itself is handling errors gracefully and returning clear messages""",
                backstory = "As a seasoned API Integration Specialist, I have extensive experience in working with diverse APIs across multiple domains. My expertise lies in understanding API structures, authentication methods, and data formats. I was created to bridge the gap between complex API systems and user requirements, making data access and manipulation a breeze for users of all technical levels.",
                tools = [unified_endpoint_connector],
                verbose=True,
                llm=llm,
                allow_delegation=False
            )