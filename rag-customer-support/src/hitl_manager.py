import json
from datetime import datetime

class HITLManager:
    def __init__(self, escalation_queue_file="escalations.json"):
        self.escalation_queue_file = escalation_queue_file
    
    def create_escalation_ticket(self, state) -> dict:
        """Create escalation ticket"""
        ticket = {
            "ticket_id": f"ESC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "query": state["query"],
            "llm_response": state.get("response", ""),
            "confidence_score": state.get("confidence_score", 0.0),
            "context_used": state.get("context", "")[:500],
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "human_response": None
        }
        
        self._save_ticket(ticket)
        return ticket
    
    def get_pending_escalations(self):
        """Retrieve pending escalations"""
        try:
            with open(self.escalation_queue_file, 'r') as f:
                data = json.load(f)
                return [t for t in data if t["status"] == "pending"]
        except FileNotFoundError:
            return []
    
    def resolve_escalation(self, ticket_id, human_response):
        """Resolve escalation with human response"""
        tickets = self._load_tickets()
        for ticket in tickets:
            if ticket["ticket_id"] == ticket_id:
                ticket["status"] = "resolved"
                ticket["human_response"] = human_response
                ticket["resolved_at"] = datetime.now().isoformat()
        self._save_tickets(tickets)
    
    def _save_ticket(self, ticket):
        tickets = self._load_tickets()
        tickets.append(ticket)
        self._save_tickets(tickets)
    
    def _load_tickets(self):
        try:
            with open(self.escalation_queue_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def _save_tickets(self, tickets):
        with open(self.escalation_queue_file, 'w') as f:
            json.dump(tickets, f, indent=2)
