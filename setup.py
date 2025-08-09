import os 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from typing import Dict, List
from langgraph.graph.message import MessagesState
from tavily import TavilyClient

load_dotenv('config.env')
assert os.getenv('OPENAI_API_KEY') is not None
assert os.getenv('TAVILY_API_KEY') is not None

OPENAI_BASE_URL = "https://openai.vocareum.com/v1"

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,
    base_url = OPENAI_BASE_URL,
	api_key= os.getenv('OPENAI_API_KEY'),
)

class State(MessagesState):
    topic: str
    summary: str
    quiz_question: str
    user_choice: str
    user_answer: str
    expected_answer: str
    dataset: List
    results: Dict
    grade: str

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

