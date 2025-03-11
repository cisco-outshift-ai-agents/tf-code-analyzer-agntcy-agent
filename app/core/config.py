import os
from typing import Any, List, Optional, Union, Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import AzureChatOpenAI

import logging


def parse_cors(v: Any) -> Union[List[str], str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    # Application settings
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    PROJECT_NAME: str = "Terraform Code Analyzer Agent"
    DESCRIPTION: str = "Application to run linters on Terraform code"
    TF_CODE_ANALYZER_HOST: str = "127.0.0.1"
    TF_CODE_ANALYZER_PORT: int = 8123
    DESTINATION_FOLDER: str = "/tmp"

    # Langchain settings (optional)
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_ENDPOINT: Optional[str] = None
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None

    # Mandatory LLM settings
    LLM_PROVIDER: str = "azure"  # or "openai"
    OPENAI_TEMPERATURE: float = 0.7
 
    # Azure settings
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = "gpt-4o"
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_API_VERSION: Optional[str] = None

    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_VERSION: Optional[str] = "gpt-4o"
    
    # Validate LLM settings
    @model_validator(mode="after")
    def check_required_settings(self) -> "Settings":
        logger = logging.getLogger(__name__)
        logger.info("Running model validator for Settings...")
        provider = self.LLM_PROVIDER.lower()
        if provider == "azure":
            missing = []
            if not self.AZURE_OPENAI_ENDPOINT:
                missing.append("AZURE_OPENAI_ENDPOINT")
            if not self.AZURE_OPENAI_API_KEY:
                missing.append("AZURE_OPENAI_API_KEY")
            if not self.AZURE_OPENAI_API_VERSION:
                missing.append("AZURE_OPENAI_API_VERSION")
            if missing:
                raise ValueError(
                    f"Missing required Azure OpenAI environment variables: {', '.join(missing)}"
                )
        elif provider == "openai":
            if not self.OPENAI_API_KEY:
                raise ValueError("Missing required OpenAI environment variable: OPENAI_API_KEY")
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        return self

    class Config:
        env_file = ".env"
        extra = "ignore"  # This will ignore any extra environment variables.

settings = Settings()


def get_llm_chain():
    """
    Get the LLM provider based on the configuration.
    """
    provider = settings.LLM_PROVIDER.lower()
    temperature = settings.OPENAI_TEMPERATURE
    if provider == "azure":
        return AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            openai_api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            temperature=temperature
        )
    elif provider == "openai":
        return ChatOpenAI(
            model_name=settings.OPENAI_API_VERSION,
            api_key=settings.OPENAI_API_KEY,
            temperature=temperature
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
