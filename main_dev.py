import json
from dotenv import load_dotenv
import os

from crewai import Crew, Process
from src.agent import OpenAPIAgent
from src.task import OpenAPITask


# Replace 'your_file.json' with the name of your JSON file
filename = 'openapi.json'

# Open and read the JSON file
with open(filename, 'r') as file:
    data = json.load(file)


class OpenAPICrew:
    def __init__(self, request):
        self.request = request

    def run(self):

        agents = OpenAPIAgent()
        tasks = OpenAPITask()

        #agents
        openapi_analyst_agent = agents.openapi_analyst_agent()
        user_request_interpreter_agent = agents.user_request_interpreter_agent()
        api_call_agent = agents.api_call_agent()

        #task
        openapi_analyst_task = tasks.openapi_analyst_task(
            openapi_analyst_agent
        )

        interpret_user_request_task = tasks.interpret_user_request_task(
            user_request_interpreter_agent,
            self.request
        )

        api_call_task = tasks.api_call_task(
            api_call_agent
        )

        #crew
        crew = Crew(
                    agents=[openapi_analyst_agent, user_request_interpreter_agent, api_call_agent],
                    #tasks=[analyze_openapi_task, interpret_user_request_task, api_call_task],
                    proccess = Process.sequential,
                    verbose=True
                    )
        
        result = crew.kickoff()
        return result
    

if __name__ == "__main__":
    print("OpenAPI Agent")
    print("------------------------------------")
    
