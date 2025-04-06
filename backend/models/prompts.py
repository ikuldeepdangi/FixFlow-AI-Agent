ROUTING_PROMPT = """
You're an AI routing assistant. Based on the following customer message, extract the following:
1. Intent
2. Priority level (low, medium, high)
3. Tone (neutral, frustrated, angry, happy)

Return in JSON format:
{{
  "intent": "...",
  "priority": "...",
  "tone": "..."
}}

User message: "{user_message}"
"""
