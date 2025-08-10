import json

from IPython.display import Image, display
from langchain_core.messages.tool import ToolMessage

def print_img(graph, filename):
    # Option 1: Create a file image
    img = Image(
        graph.get_graph().draw_mermaid_png()
    )
    image_filename = f"{filename}.png"
    with open(image_filename, "wb") as f:
        f.write(img.data)

    # Option 2: Display Image
    display(
        Image(
            graph.get_graph().draw_mermaid_png()
        )
    )


def get_grade(result: dict) -> str:
    """
    Grade answer using faithfulness, factual_correctness, answer_relevancy, and semantic_similarity.
    Returns one of: A, B, C, D
    """

    weights = {
        "faithfulness": 0.3,
        "factual_correctness": 0.3,
        "answer_relevancy": 0.2,
        "semantic_similarity": 0.2,
    }

    faithfulness = result.get("faithfulness", 0.0)
    factual_correctness = result.get("factual_correctness(mode=f1)", 0.0)
    relevancy = result.get("answer_relevancy", 0.0)
    semantic_similarity = result.get("semantic_similarity", 0.0)

    weighted_score = (
        faithfulness * weights["faithfulness"] +
        factual_correctness * weights["factual_correctness"] +
        relevancy * weights["answer_relevancy"] +
        semantic_similarity * weights["semantic_similarity"]
    )
    grade = ""
    if weighted_score >= 0.85:
        grade= "A"
    elif weighted_score >= 0.7:
        grade= "B"
    elif weighted_score >= 0.5:
        grade= "C"
    else:
        grade= "D"
    
    return grade

def get_tools_message_content(msg:ToolMessage)->str:
    data = json.loads(msg.content)

    all_content = "\n".join(
        item["content"] for item in data.get("results", []) if item.get("content")
    )

    return all_content