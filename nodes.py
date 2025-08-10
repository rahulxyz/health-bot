
from langgraph.graph import END

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

from ragas import EvaluationDataset
from ragas.evaluation import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness, FactualCorrectness, AnswerRelevancy, SemanticSimilarity

from typing import Dict
from helpers import get_grade, get_tools_message_content
from setup import State, llm, tavily_client

def entry_point(state: State):
    state = reset_state(state=state)
    print("What health topic or medical condition would you like to learn about?")
    topic=input()
    system_message = SystemMessage("You conduct web search from reputable sources only to response to user's question.")
    human_message = HumanMessage(topic)
    messages = [system_message, human_message]
    return {
        "messages": messages,
        "topic": topic
    }

@tool
def web_search(topic: str)->Dict:
    """
    Return top search results from reputable medical sources for a given search query
    """
    response = tavily_client.search(topic)
    return response

llm_with_tools = llm.bind_tools([web_search])

def agent(state: State):
    messages = state["messages"]
    ai_message = llm_with_tools.invoke(messages)
    messages.append(ai_message)
        
    return {"messages": messages}

def router(state: State):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    
    return END

def summarize(state: State):
    messages = state["messages"]
    tools_content = get_tools_message_content(messages[-1])
    summarization_prompt = f"""
    Summarise the previous search result into 3 to 4 paragraphs. 
    Avoid making assumptions. Summary should be simple and patient friendly
    Ensure the summary's information source remains limited to following context: {tools_content}
    """
    sys_message= SystemMessage(content=summarization_prompt)
    messages.append(sys_message)
    ai_message = llm.invoke(messages)
    messages.append(ai_message)
    return {"messages": messages, "summary": ai_message.content}

def ask_user(state:State):
    print("\nWould you like to test your knowledge? Yes or No")
    user_choice = input()
    return {"user_choice": user_choice}

def quiz_router(state: State):
    user_choice = state["user_choice"]

    if user_choice.lower() == "yes":
        return "prepare_quiz"
    
    return END

def prepare_quiz(state: State):
    messages = state["messages"]
    summary = state["summary"]
    quiz_prompt = f"Ask user a quiz subjective question that is answerable after reading this summary: {summary}"
    sys_message = SystemMessage(content=quiz_prompt)
    messages.append(sys_message)
    ai_message = llm_with_tools.invoke(messages)
    messages.append(ai_message)
    return {"messages": messages, "quiz_question": ai_message.content}

def prepare_for_evaluation(state: State):
    messages = state["messages"]
    user_answer = input()
    summary = state["summary"]
    quiz_question = state["quiz_question"]
    quiz_summary_answer_prompt = f"Answer the question based only on the following context:{summary}. Question: {quiz_question}"
    sys_message=SystemMessage(content=quiz_summary_answer_prompt)
    messages.append(sys_message)
    ai_message = llm.invoke(messages)
    expected_answer = ai_message.content
    messages.append(ai_message)

    dataset=[]
    dataset.append(
        {
            "user_input": quiz_question,
            "retrieved_contexts": [summary],
            "response": user_answer,
            "reference": expected_answer,
        }
    )
    return { "messages": messages, "dataset": dataset }

def evaluater(state: State):
    dataset = state["dataset"]
    user_answer = dataset[0]["response"]
    messages = state["messages"]
    expected_answer = dataset[0]["reference"]
    evaluation_dataset = EvaluationDataset.from_list(dataset)
    evaluator_llm = LangchainLLMWrapper(llm)

    result = evaluate(
        dataset=evaluation_dataset,
        metrics=[
            FactualCorrectness(),
            Faithfulness(),
            AnswerRelevancy(),
            SemanticSimilarity()
        ],
        llm=evaluator_llm,
    )
    df = result.to_pandas()
    results_dict = df.to_dict(orient="records")[0]
    grade = get_grade(results_dict)

    return {
        "messages": messages, 
        "user_answer": user_answer, 
        "messages":messages, 
        "expected_answer": expected_answer,
        "results": results_dict,
        "grade": grade
    }

def justify_grade(state: State):
    grade=state["grade"]
    results = state["results"]
    user_answer = state["user_answer"]
    summary = state["summary"]
    messages = state["messages"]
    justify_prompt = f"""Justify the grade:{grade} and evaluation: {results}, given to user's answer: {user_answer}. Don't mention exact points received 
    Include a citation referencing: {summary} by stating as cited here and break into multiple points.
    Follow following format:
    You have received grade [x] for the following reasons:
    """
    sys_message = SystemMessage(content=justify_prompt)
    messages.append(sys_message)
    ai_message = llm.invoke(messages)
    messages.append(ai_message)
    return {"messages": messages}

def ask_user_restart(state:State):
    print("\nDo you want to learn about new health topic again? yes or no")
    choice = input()
    return {"user_choice": choice}

def restart_router(state:State):
    choice = state["user_choice"]
    if choice.lower() == 'yes':
        return "entry_point"

    return END

def reset_state(state: State) -> State:
    return State(
        messages=[],
        topic=None,
        summary=None,
        quiz_question=None,
        user_choice=None,
        user_answer=None,
        expected_answer=None,
        dataset=None,
        results=None,
        grade=None
    )