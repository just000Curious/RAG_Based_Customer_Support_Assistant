from typing import Literal
from .graph_state import QueryState

def should_escalate(state: QueryState) -> Literal["escalate", "respond"]:
    """Determine if human intervention needed"""
    
    if state.get("confidence_score", 1.0) < 0.6:
        return "escalate"
    
    if state.get("intent") == "unknown":
        return "escalate"
    
    if not state.get("retrieved_docs"):
        return "escalate"
    
    complex_keywords = ["refund", "complaint", "damaged", "escalate"]
    if any(keyword in state["query"].lower() for keyword in complex_keywords):
        return "escalate"
    
    return "respond"

def detect_intent(query: str) -> str:
    """Route based on query intent"""
    intents = {
        "product": ["specifications", "features", "compatible"],
        "return": ["return", "refund", "exchange"],
        "technical": ["error", "not working", "issue"],
    }
    
    for intent, keywords in intents.items():
        if any(keyword in query.lower() for keyword in keywords):
            return intent
    return "general"
