# backend/intent_router.py

from sentence_transformers import SentenceTransformer, util

# Load the model once (lightweight model for speed)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Predefined intents and examples (can be expanded)
intent_examples = {
    "Order Not Delivered": ["I didn’t get my package", "My order hasn’t arrived", "Item not delivered"],
    "Wrong Item Received": ["I got the wrong item", "This isn’t what I ordered", "Received a different product"],
    "Refund Request": ["I want my money back", "Need a refund", "How can I get a refund"],
    "Technical Issue": ["App not working", "Getting an error", "There’s a bug in the system"],
    "Cancel Order": ["I want to cancel my order", "Please cancel the purchase", "Can I stop this order"],
    "Account/Login Problems": ["I can’t log in", "Account is locked", "Login not working"]
}

intent_to_team = {
    "Order Not Delivered": "Logistics",
    "Wrong Item Received": "Logistics",
    "Refund Request": "Payments",
    "Technical Issue": "Tech Support",
    "Cancel Order": "Orders Team",
    "Account/Login Problems": "Account Support"
}

def detect_intent(user_input: str):
    best_score = -1
    best_intent = "General Inquiry"

    for intent, examples in intent_examples.items():
        for ex in examples:
            sim = util.cos_sim(model.encode(user_input), model.encode(ex)).item()
            if sim > best_score:
                best_score = sim
                best_intent = intent

    assigned_team = intent_to_team.get(best_intent, "General Support")
    return best_intent, assigned_team
