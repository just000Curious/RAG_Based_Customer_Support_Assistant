from typing import TypedDict, List, Optional, Literal
from pydantic import BaseModel

class QueryState(TypedDict):
    query: str
    retrieved_docs: List[str]
    context: str
    response: str
    confidence_score: float
    needs_escalation: bool
    intent: Literal["general", "product", "return", "technical", "unknown"]
    human_feedback: Optional[str]
