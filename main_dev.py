import json
from dotenv import load_dotenv
import os

from crewai import Crew, Process
from src.agent import openapi_analyst_agent, user_request_interpreter_agent, api_call_agent
from src.task import analyze_openapi_task, interpret_user_request_task, api_call_task


# Replace 'your_file.json' with the name of your JSON file
filename = 'openapi.json'

# Open and read the JSON file
with open(filename, 'r') as file:
    data = json.load(file)


#crew
crew = Crew(
    agents=[openapi_analyst_agent, user_request_interpreter_agent, api_call_agent],
    tasks=[analyze_openapi_task, interpret_user_request_task, api_call_task],
    proccess = Process.sequential,
    verbose=True
)

result = crew.kickoff(inputs={"data": data,
                            "request":"Give me details of item_number 112"})
print(result)