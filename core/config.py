from pydantic import SecretStr, BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

from ai.prompts.summary_llm_prompt import (
    SUMMARY_SYSTEM_PROMPT,
    SUMMARY_USER_TEMPLATE,
)


class PromptSettings(BaseModel):
    summary_system_prompt: str = SUMMARY_SYSTEM_PROMPT
    summary_user_template: str = SUMMARY_USER_TEMPLATE


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    anthropic_api_key:SecretStr
    openai_api_key:SecretStr
    voyageai_api_key:SecretStr


    database_url:str

    debug:bool = False
    request_timeout:int = 30

    rerank_model:str = "rerank-2.5"

    repo_owner:str
    repo_name:str

    github_pat_key:str

    prompts: PromptSettings = Field(default_factory=PromptSettings)


@lru_cache
def get_settings() -> Settings:
    return Settings()
