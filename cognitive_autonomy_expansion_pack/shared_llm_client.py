"""
Shared LLM Client for Cognitive Autonomy Expansion Pack
Provides unified LLM access across all cognitive modules
"""

import os
import time
from typing import Optional
from openai import OpenAI
from langchain_openai import ChatOpenAI


class SharedLLMClient:
    """Shared LLM client for all Cognitive Autonomy modules"""

    def __init__(self, model="gpt-4o-mini"):
        # Create OpenAI client
        self.openai_client = OpenAI()

        # Wrap with LangChain
        self.llm = ChatOpenAI(
            model=model,
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )

    def invoke(self, prompt: str, correlation_id: Optional[str] = None) -> str:
        """Invoke LLM with proper error handling and logging"""
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"LLM invocation failed: {e}")
            return f"[LLM_ERROR: {str(e)}]"


# Global shared instance
_shared_llm = None


def get_shared_llm():
    """Get or create shared LLM instance"""
    global _shared_llm
    if _shared_llm is None:
        _shared_llm = SharedLLMClient()
    return _shared_llm
