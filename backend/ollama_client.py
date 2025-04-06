import requests

def chat_with_ollama(message: str) -> str:
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": message,
        "stream": True
    }, stream=True)

    output = ""
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode('utf-8'))
                output += data.get("response", "")
            except Exception as e:
                print("JSON decode error:", e)
                print("Line was:", line)
    return output
