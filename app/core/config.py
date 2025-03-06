import os
from typing import Any, Literal

from pydantic_settings import BaseSettings
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import AzureChatOpenAI



def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)

def get_llm_chain():
    """
    Get the LLM provider based on the configuration.
    """
    llm_provider = os.getenv("LLM_PROVIDER", "azure").lower()
    temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.7))
    if llm_provider == "azure":
        return AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            temperature=temperature
        )
    elif llm_provider== "openai":
        return ChatOpenAI(
            model_name=os.getenv("OPENAI_API_VERSION", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=temperature
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")

class Settings(BaseSettings):

    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    PROJECT_NAME: str = "Terraform Code Analyzer Agent"
    DESCRIPTION: str = "Application to run linters on Terraform code"


settings = Settings()  # type: ignore
