from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import subprocess
import os
import sys
import io
import sqlite3

# Force UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to frontend static files
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))

# Validate frontend path
if not os.path.exists(os.path.join(frontend_path, "index.html")):
    raise FileNotFoundError(f"index.html not found in {frontend_path}")

# Mount static files under /static instead of /
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Serve index.html at root
@app.get("/")
def serve_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# Admin panel route
@app.get("/admin")
def serve_admin():
    return FileResponse(os.path.join(frontend_path, "admin.html"))

# Initialize DB
from db import init_db, save_chat_log
init_db()

# Request schema
class MessageRequest(BaseModel):
    message: str

# LLM wrapper
def get_chat_response(user_input: str) -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=user_input,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            errors='replace'
        )
        if result.stderr:
            print("[stderr]", result.stderr)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Logging interaction
def log_interaction(user_msg: str, ai_reply: str):
    print(f"\n🧑 {user_msg}\n🤖 {ai_reply}\n")

# Core logic
from summarizer import summarize_and_extract_actions
from router import get_ticket_routing

@app.post("/get_response/")
async def get_response(request: MessageRequest):
    user_input = request.message

    # Summarize + Extract Actions
    summary, action_list = summarize_and_extract_actions(user_input)

    # Generate LLM Response
    llm_response = get_chat_response(user_input)

    # Routing Intelligence
    routing_info = get_ticket_routing(user_input) or {}

    # Safely extract routing details with fallback values
    emotions = routing_info.get("emotions", [])
    intent = routing_info.get("intent", "unknown")
    assigned_agent = routing_info.get("assigned_agent", "general_support_agent")
    assigned_team = routing_info.get("assigned_team", "general_support_team")
    tags = routing_info.get("tags", [])

    # Log interaction
    log_interaction(user_input, llm_response)

    # Save to DB
    save_chat_log(
        user_input=user_input,
        ai_response=llm_response,
        summary=summary,
        actions=action_list,
        intent=intent,
        assigned_team=assigned_team,
        assigned_agent=assigned_agent,
        emotions=emotions,
        tags=tags
    )

    # Return structured response
    return JSONResponse({
        "response": llm_response,
        "summary": summary,
        "actions": action_list,
        "intent": intent,
        "assigned_agent": assigned_agent,
        "assigned_team": assigned_team,
        "emotions": emotions,
        "tags": tags
    })

# Admin logs
@app.get("/admin/logs")
def get_logs():
    conn = sqlite3.connect("chat_logs.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat_logs ORDER BY timestamp DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return {"logs": [dict(row) for row in rows]}

# Vector-based search
from vector_store import TicketVectorStore

@app.get("/api/similar_tickets")
def search_similar(query: str):
    store = TicketVectorStore()
    results = store.search_similar_tickets(query)
    return {"similar_tickets": results}

# Optional simple chat API
@app.post("/api/chat")
async def chat(request: MessageRequest):
    try:
        response_text = get_chat_response(request.message)
        return {"response": response_text}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

# Routing API
@app.post("/route-message")
def route_message(data: dict):
    message = data.get("message")
    if not message:
        return {"error": "No message provided"}
    routing_info = get_ticket_routing(message)
    return routing_info
