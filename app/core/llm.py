"""LLM Factory."""

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from langchain_openai import ChatOpenAI


def get_llm() -> ChatOpenAI:
    """Initializes and returns the ChatOpenAI client configured for gpt-6-luna."""
    return ChatOpenAI(
        model=OPENAI_MODEL,
        api_key=OPENAI_API_KEY,
        reasoning_effort="low",
    )