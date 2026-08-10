from functools import lru_cache

from anthropic import Anthropic
from core.config import get_settings

settings = get_settings()


@lru_cache
def get_anthropic_client() -> Anthropic:
    return Anthropic(api_key=settings.anthropic_api_key.get_secret_value())


def summarize_original_question(title: str, original_question: str) -> str:
    client = get_anthropic_client()
    summary_system_prompt = settings.prompts.summary_system_prompt.format(repo=f"{settings.repo_owner}/{settings.repo_name}")
    summary_user_template = settings.prompts.summary_user_template.format(title=title, original_question=original_question)

    resp = client.messages.create(
        model="claude-haiku-4-5",
        temperature=0,
        max_tokens=256,
        system=summary_system_prompt,
        messages=[{"role": "user", "content": summary_user_template}]
    )

    return resp.content[0].text
