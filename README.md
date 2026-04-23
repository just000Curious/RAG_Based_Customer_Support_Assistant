# RAG-Based Customer Support Assistant

This project is a powerful, local Retrieval-Augmented Generation (RAG) chatbot built to handle customer support inquiries. It uses Groq, LangGraph, and ChromaDB to ingest custom PDF knowledge bases and answer user queries, seamlessly escalating complex issues to a human agent when needed.

## Features
- **Dynamic PDF Uploads**: Directly upload your support PDFs through the UI.
- **Contextual Answers**: Generates answers strictly based on your uploaded document using the lightning-fast `Groq` API (`llama-3.3-70b-versatile`).
- **Intelligent Routing**: Uses `LangGraph` to dynamically route intents. If the bot is unsure or the user is frustrated, it triggers an escalation.
- **Human-in-the-Loop (HITL)**: A dedicated Agent Dashboard to review and manually resolve escalated queries.
- **100% Local Vector Store**: Uses HuggingFace local embeddings (`all-MiniLM-L6-v2`) and ChromaDB to persist document embeddings locally, completely avoiding API rate limits.

---

## 🛠️ Installation & Setup

1. **Clone the repository and enter the directory**:
   ```bash
   cd rag-customer-support
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install langchain-groq langchain_text_splitters
   ```

4. **Environment Variables**:
   Create a `.env` file in the root directory and add your Groq API Key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   CHROMA_PERSIST_DIR=./chroma_db
   ```

---

## 🚀 How to Run the App

Launch the application using Streamlit:
```bash
streamlit run app.py
```
This will open the web interface in your default browser at `http://localhost:8501`.

---

## 💡 How to Use It

1. **Upload a Knowledge Base**: 
   - Look at the sidebar on the left and upload any PDF file (e.g., a product manual or company return policy).
   - The system will automatically chunk the document, generate embeddings, and load it into the bot's memory.

2. **Chat with the Bot**: 
   - Type your customer support query in the main chat window. 
   - The bot will retrieve relevant paragraphs from the PDF and formulate a helpful response.

3. **Triggering Escalations**: 
   - Ask a question completely outside the scope of the PDF or type something like *"I want to speak to a human manager immediately"*.
   - The bot will recognize the intent or lack of context and escalate the ticket.

4. **Human-in-the-Loop Dashboard**: 
   - In the sidebar, click **Refresh Escalations**.
   - You will see the pending tickets. A human agent can review the user's query and the bot's attempted response, then resolve the ticket manually!

---

## 🧠 How It Works Internally

1. **Document Processing**: When a PDF is uploaded, LangChain splits the text into small overlapping chunks.
2. **Embeddings**: Local `HuggingFaceEmbeddings` (`all-MiniLM-L6-v2`) creates vector representations of these chunks, which are stored in ChromaDB without any API costs or limits.
3. **Retrieval**: When a user asks a question, ChromaDB fetches the top most relevant chunks.
4. **Generation & Orchestration**: 
   - The system uses **LangGraph** to model the flow as a state machine.
   - The retrieved context and user query are passed to the blazing fast `Groq` LLM.
   - A routing layer evaluates the confidence and intent of the generated response.
   - If the bot cannot find the answer in the text, it transitions to the **Escalate Node**, which dumps the interaction into `escalations.json` for human review.
