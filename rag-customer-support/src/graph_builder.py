from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .graph_state import QueryState
from .routing_logic import should_escalate

class GraphBuilder:
    def __init__(self, nodes):
        self.nodes = nodes
        self.graph = StateGraph(QueryState)
    
    def build(self):
        # Add nodes
        self.graph.add_node("retrieve", self.nodes.retrieve_node)
        self.graph.add_node("generate", self.nodes.generate_node)
        self.graph.add_node("escalate", self.nodes.escalate_node)
        
        # Add edges
        self.graph.add_edge("retrieve", "generate")
        
        # Conditional routing
        self.graph.add_conditional_edges(
            "generate",
            should_escalate,
            {
                "respond": END,
                "escalate": "escalate"
            }
        )
        
        self.graph.add_edge("escalate", END)
        self.graph.set_entry_point("retrieve")
        
        return self.graph.compile(checkpointer=MemorySaver())
