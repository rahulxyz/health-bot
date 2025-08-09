from langgraph.prebuilt import ToolNode
from langgraph.graph import START, END, StateGraph

from helpers import print_img
from setup import State
from nodes import entry_point, agent, web_search, summarize, ask_user_restart, prepare_quiz, prepare_for_evaluation, evaluater, justify_grade, ask_user, router, quiz_router, restart_router

workflow = StateGraph(State)
workflow.add_node("entry_point", entry_point)
workflow.add_node("agent", agent)
workflow.add_node("tools", ToolNode([web_search]))
workflow.add_node("summarize",summarize)
workflow.add_node("ask_user_restart",ask_user_restart)
workflow.add_node("prepare_quiz", prepare_quiz)
workflow.add_node("prepare_for_evaluation",prepare_for_evaluation)
workflow.add_node("evaluater",evaluater)
workflow.add_node("justify_grade",justify_grade)
workflow.add_node("ask_user",ask_user)
workflow.add_edge(START, "entry_point")
workflow.add_edge("entry_point", "agent")
workflow.add_conditional_edges(
    source="agent",
    path=router,
    path_map=["tools", END]
)
workflow.add_edge("tools", "summarize")
workflow.add_edge("summarize", "ask_user")
workflow.add_conditional_edges(
    source="ask_user",
    path=quiz_router,
    path_map=["prepare_quiz", END]
)

workflow.add_edge("prepare_quiz", "prepare_for_evaluation")
workflow.add_edge("prepare_for_evaluation","evaluater")
workflow.add_edge("evaluater", "justify_grade")
workflow.add_edge("justify_grade", "ask_user_restart")

workflow.add_conditional_edges(
    source="ask_user_restart",
    path=restart_router,
    path_map=["entry_point", END]
)

graph = workflow.compile()
print_img(graph, "main")
state = State(
    messages=[]
)

for event in graph.stream(input=state, stream_mode="values"):
    if not event['messages']:
        continue
    event['messages'][-1].pretty_print()
