import json
from dotenv import load_dotenv
import os

from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
import requests



# Replace 'your_file.json' with the name of your JSON file
filename = 'openapi.json'

# Open and read the JSON file
with open(filename, 'r') as file:
    data = json.load(file)

# Now 'data' contains the parsed JSON data
print(data)


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

print(llm)