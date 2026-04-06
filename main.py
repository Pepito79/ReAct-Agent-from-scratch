import sys,os
sys.path.append('..')
from openai import OpenAI
from dotenv import load_dotenv
from src.Agent import Agent

def main():
    load_dotenv()
    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "ReAct Agent",
    }
)
    agent = Agent(client, stream=True)
    return agent

if __name__ == "__main__":
    agent = main()
    agent.chat()
    
