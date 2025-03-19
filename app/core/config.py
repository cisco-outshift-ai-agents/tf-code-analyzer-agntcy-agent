import logging
from typing import Any, List, Optional, Union

from langchain_openai import ChatOpenAI
from langchain_openai import AzureChatOpenAI
from pydantic_settings import BaseSettings

# Error messages
INTERNAL_ERROR_MESSAGE = "An unexpected error occurred. Please try again later."


def parse_cors(v: Any) -> Union[List[str], str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    if isinstance(v, (list, str)):
        return v
    raise ValueError(v)

class APISettings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Terraform Code Analyzer Agent"
    DESCRIPTION: str = "Application to run linters on Terraform code"
    TF_CODE_ANALYZER_HOST: str = "127.0.0.1"
    TF_CODE_ANALYZER_PORT: int = 8123

class AppSettings(BaseSettings):
    DESTINATION_FOLDER: str = "/tmp"

    # Langchain settings (optional)
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_ENDPOINT: Optional[str] = None
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None

    # Mandatory LLM settings
    OPENAI_TEMPERATURE: Optional[float] = 0.7

    # Azure settings
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_API_VERSION: Optional[str] = None

    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_VERSION: Optional[str] = "gpt-4o"

    class Config:
        extra = "ignore"  # This will ignore any extra environment variables.

def load_and_validate_app_settings() -> AppSettings:
    """
    Loads and validates application settings at startup.
    """
    settings = AppSettings()
    logger = logging.getLogger(__name__)

    missing_azure = [
        key for key, value in {
            "AZURE_OPENAI_ENDPOINT": settings.AZURE_OPENAI_ENDPOINT,
            "AZURE_OPENAI_API_KEY": settings.AZURE_OPENAI_API_KEY,
            "AZURE_OPENAI_DEPLOYMENT_NAME": settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            "AZURE_OPENAI_API_VERSION": settings.AZURE_OPENAI_API_VERSION,
        }.items() if not value
    ]

    missing_openai = ["OPENAI_API_KEY"] if not settings.OPENAI_API_KEY else []
    if missing_azure and missing_openai:
        raise ValueError(
            f"Missing required LLM settings. Either provide:"
            f" OpenAI fields: {', '.join(missing_openai)}"
            f" OR Azure OpenAI fields: {', '.join(missing_azure)}"
        )   
    elif not(missing_azure or missing_openai):
        raise ValueError(
            "Both OpenAI and Azure OpenAI settings are provided. Please provide only one."
        )

    logger.info("Settings validated successfully.")
    return settings


def get_llm_chain(settings : AppSettings) -> Union[ChatOpenAI, AzureChatOpenAI]:
    """
    Get the LLM provider based on the available configuration.
    Automatically determines if Azure OpenAI or OpenAI should be used.
    """
    temperature = settings.OPENAI_TEMPERATURE

    # Check if Azure settings are provided
    has_azure_settings = all([
        settings.AZURE_OPENAI_ENDPOINT,
        settings.AZURE_OPENAI_DEPLOYMENT_NAME,
        settings.AZURE_OPENAI_API_KEY,
        settings.AZURE_OPENAI_API_VERSION
    ])

    # Check if OpenAI settings are provided
    has_openai_settings = settings.OPENAI_API_KEY is not None

    if has_azure_settings:
        return AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            openai_api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            temperature=temperature,
        )

    if has_openai_settings:
        return ChatOpenAI(
            model_name=settings.OPENAI_API_VERSION,
            api_key=settings.OPENAI_API_KEY,
            temperature=temperature,
        )
    
    return ValueError("No valid LLM settings found.")
