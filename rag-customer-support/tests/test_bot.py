import pytest
from main import CustomerSupportBot
import os

test_queries = {
    "general": "What are your shipping options?",
    "product": "Tell me about product specifications",
    "return": "How do I return a damaged item?",
    "technical": "My device won't turn on",
    "edge_case": "What's the meaning of life?",  # Should escalate
}

@pytest.mark.asyncio
async def test_all_intents():
    if not os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY") == "your_api_key_here":
        pytest.skip("No valid Google API key provided.")
    
    bot = CustomerSupportBot()
    bot.initialize()
    
    for intent, query in test_queries.items():
        result = await bot.process_query(query)
        assert result["response"] is not None
        print(f"{intent}: Needs Escalation: {result['needs_escalation']}")
