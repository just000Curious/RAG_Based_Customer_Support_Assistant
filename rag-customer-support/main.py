import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from src.document_processor import DocumentProcessor
from src.embedding_manager import EmbeddingManager
from src.graph_nodes import GraphNodes
from src.graph_builder import GraphBuilder
from src.routing_logic import detect_intent
from src.hitl_manager import HITLManager

load_dotenv()

class CustomerSupportBot:
    def __init__(self, pdf_path=None):
        self.pdf_path = pdf_path or os.getenv("PDF_PATH")
        self.llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
        self.processor = DocumentProcessor(self.pdf_path)
        self.embedding_manager = EmbeddingManager()
        self.vector_store = None
        self.graph = None
        self.hitl = HITLManager()
    
    def initialize(self):
        """Initialize the entire system"""
        print("Loading documents...")
        docs = self.processor.load_documents()
        
        print("Chunking documents...")
        chunks = self.processor.chunk_documents(docs)
        
        print("Creating embeddings and vector store...")
        self.vector_store = self.embedding_manager.create_vector_store(chunks)
        
        print("Building LangGraph workflow...")
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
        nodes = GraphNodes(retriever, self.llm)
        graph_builder = GraphBuilder(nodes)
        self.graph = graph_builder.build()
        
        print("System ready!")
    
    async def process_query(self, query: str, thread_id: str = "1") -> dict:
        """Process a user query through the graph"""
        initial_state = {
            "query": query,
            "retrieved_docs": [],
            "context": "",
            "response": "",
            "confidence_score": 0.0,
            "needs_escalation": False,
            "intent": detect_intent(query),
            "human_feedback": None
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        result = await self.graph.ainvoke(initial_state, config=config)
        
        return {
            "query": query,
            "response": result.get("response", ""),
            "needs_escalation": result.get("needs_escalation", False),
            "confidence": result.get("confidence_score", 0.0)
        }
    
    def check_escalations(self):
        """Check pending escalations"""
        return self.hitl.get_pending_escalations()
