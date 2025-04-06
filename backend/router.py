from models.prompts import ROUTING_PROMPT
from ollama_client import chat_with_ollama  # replace with your actual method


def parse_response(response: str) -> dict:
    import json
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"intent": "unknown", "priority": "medium", "tone": "neutral"}


def route_based_on_intent(info: dict) -> str:
    intent = info.get("intent", "").lower()
    priority = info.get("priority", "medium")
    tone = info.get("tone", "neutral")

    if priority == "high" and tone in ["angry", "frustrated"]:
        return "escalation_manager"

    match intent:
        case "cancel order":
            return "orders_agent"
        case "track order":
            return "logistics_agent"
        case "technical issue" | "bug report":
            return "tech_support_agent"
        case "billing query":
            return "billing_agent"
        case _:
            return "general_support_agent"


def get_ticket_routing(message: str) -> dict:
    message_lower = message.lower()

    if "login" in message_lower or "password" in message_lower:
        return {
            "intent": "login_issue",
            "assigned_agent": "general_support_agent",
            "assigned_team": "login_support",
            "emotions": ["frustrated"],
            "tags": ["auth", "login"]
        }
    elif "payment" in message_lower:
        return {
            "intent": "payment_issue",
            "assigned_agent": "billing_team",
            "assigned_team": "payments",
            "emotions": ["concerned"],
            "tags": ["billing"]
        }

    return {
        "intent": "unknown",
        "assigned_agent": "general_support_agent",
        "assigned_team": "general_support_team",
        "emotions": [],
        "tags": []
    }
