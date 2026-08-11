from functools import lru_cache
from langchain_anthropic import ChatAnthropic
from core.config import get_settings

@lru_cache
def get_research_llm() -> ChatAnthropic:
    settings = get_settings()
    return ChatAnthropic(
        model=settings.research_model,
        temperature=0,
        max_tokens=2048,
        api_key=settings.anthropic_api_key.get_secret_value()
    )
    
    