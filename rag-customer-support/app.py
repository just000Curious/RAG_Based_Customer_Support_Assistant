import streamlit as st
import asyncio
from main import CustomerSupportBot

st.set_page_config(page_title="Customer Support Assistant", layout="wide")

@st.cache_resource
def init_bot(pdf_path=None, version=1):
    bot = CustomerSupportBot(pdf_path=pdf_path)
    bot.initialize()
    return bot

def main():
    st.title("🤖 RAG-Based Customer Support Assistant")
    st.markdown("---")
    
    pdf_path = st.session_state.get("pdf_path", None)
    version = st.session_state.get("kb_version", 1)
    
    try:
        bot = init_bot(pdf_path, version)
    except Exception as e:
        st.error(f"Failed to initialize the bot: {e}")
        st.stop()
    
    # Sidebar for HITL dashboard
    with st.sidebar:
        st.header("📄 Knowledge Base")
        uploaded_file = st.file_uploader("Upload PDF Knowledge Base", type=["pdf"])
        if uploaded_file is not None:
            save_path = "./data/uploaded_kb.pdf"
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Reinitialize if it's a new upload or we haven't tracked it
            if st.session_state.get("pdf_path") != save_path or "kb_version" not in st.session_state:
                st.session_state.pdf_path = save_path
                st.session_state.kb_version = st.session_state.get("kb_version", 1) + 1
                st.rerun()

        st.header("📋 Human-in-the-Loop Dashboard")
        if st.button("Refresh Escalations"):
            escalations = bot.check_escalations()
            if escalations:
                for esc in escalations:
                    with st.expander(f"Ticket: {esc['ticket_id']}"):
                        st.write(f"Query: {esc['query']}")
                        st.write(f"LLM Response: {esc['llm_response']}")
                        response = st.text_area("Agent Response:", key=esc['ticket_id'])
                        if st.button(f"Resolve {esc['ticket_id']}"):
                            bot.hitl.resolve_escalation(esc['ticket_id'], response)
                            st.success("Resolved!")
            else:
                st.info("No pending escalations")
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("escalated"):
                st.warning("⚠️ This response was escalated to a human agent")
    
    # Query input
    if prompt := st.chat_input("Ask me about products, returns, or technical support..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = asyncio.run(bot.process_query(prompt))
                    st.markdown(result["response"])
                    
                    if result["needs_escalation"]:
                        st.warning("🔄 This query has been escalated to a human agent")
                    
                    st.caption(f"Confidence: {result['confidence']:.0%}")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["response"],
                        "escalated": result["needs_escalation"]
                    })
                except Exception as e:
                    st.error(f"An error occurred while processing: {e}")

if __name__ == "__main__":
    main()
