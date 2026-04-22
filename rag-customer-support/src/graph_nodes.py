from .graph_state import QueryState
from .hitl_manager import HITLManager

class GraphNodes:
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm
    
    async def retrieve_node(self, state: QueryState) -> QueryState:
        """Retrieve relevant documents"""
        docs = await self.retriever.ainvoke(state["query"])
        state["retrieved_docs"] = [doc.page_content for doc in docs]
        state["context"] = "\n\n".join(state["retrieved_docs"])
        return state
    
    async def generate_node(self, state: QueryState) -> QueryState:
        """Generate response using LLM"""
        prompt = f"""Context: {state.get('context', '')}
        
        Question: {state['query']}
        
        Answer based on the context above. If unsure, say so."""
        
        response = await self.llm.ainvoke(prompt)
        state["response"] = response.content
        state["confidence_score"] = self._calculate_confidence(response)
        return state
    
    def _calculate_confidence(self, response):
        # Simple confidence scoring
        return 0.85 if "unsure" not in response.content.lower() else 0.45

    async def escalate_node(self, state: QueryState) -> QueryState:
        """Handle escalation to human"""
        hitl = HITLManager()
        ticket = hitl.create_escalation_ticket(state)
        
        state["needs_escalation"] = True
        
        state["response"] = f"""I apologize, but I need to escalate this to a human agent.

Ticket ID: {ticket['ticket_id']}
Your query: {state['query']}

A support agent will get back to you shortly."""
        return state
