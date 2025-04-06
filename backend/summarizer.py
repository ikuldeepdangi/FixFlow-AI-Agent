from typing import Tuple
from ollama import Client

client = Client(host='http://localhost:11434')

def summarize_and_extract_actions(conversation: str) -> Tuple[str, list]:
    prompt = f"""
    You are a customer support AI. Given the following customer query or chat, do two things:
    
    1. Generate a short professional summary of the issue.
    2. Extract clear action items or next steps.
    
    Output format:
    Summary: <short summary>
    Actions:
    - <action 1>
    - <action 2>
    
    Chat:
    {conversation}
    """

    response = client.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )

    output = response["message"]["content"]

    # Split output into summary and actions
    summary_line = ""
    actions = []

    for line in output.splitlines():
        line = line.strip()
        if line.lower().startswith("summary:"):
            summary_line = line[len("summary:"):].strip()
        elif line.startswith("- "):
            actions.append(line[2:].strip())

    return summary_line, actions
