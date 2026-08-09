from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

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
    
    repo_owner:str
    repo_name:str
    
    github_pat_key:str

    
@lru_cache
def get_settings() -> Settings:
    return Settings()