"""
Configuration management for the RAG application.

Centralizes all environment variables and settings using Pydantic.
"""

import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Azure OpenAI
    azure_openai_endpoint: str = Field(
        default="",
        alias="AZURE_OPENAI_ENDPOINT",
        description="Azure OpenAI service endpoint"
    )
    azure_openai_chat_deployment: str = Field(
        default="gpt-5.4-mini",
        alias="AZURE_OPENAI_CHAT_DEPLOYMENT",
        description="Chat model deployment name"
    )
    azure_openai_api_version: str = Field(
        default="2024-10-21",
        description="Azure OpenAI API version"
    )
    
    # Azure AI Search
    azure_ai_search_endpoint: str = Field(
        default="",
        alias="AZURE_AI_SEARCH_ENDPOINT",
        description="Azure AI Search service endpoint"
    )
    azure_search_index_name: str = Field(
        default="documents",
        alias="AZURE_SEARCH_INDEX_NAME",
        description="Azure AI Search index name"
    )
    
    # RAG Configuration
    search_top_k: int = Field(
        default=5,
        description="Number of documents to retrieve"
    )
    use_semantic_ranker: bool = Field(
        default=True,
        description="Whether to use semantic ranking"
    )
    semantic_configuration_name: str = Field(
        default="default-semantic",
        description="Semantic configuration name in search index"
    )
    vector_field_name: str = Field(
        default="embedding",
        description="Name of the vector field in search index"
    )
    
    # Model parameters
    max_tokens: int = Field(
        default=2048,
        description="Maximum tokens in response"
    )
    temperature: float = Field(
        default=0.7,
        description="Sampling temperature for generation"
    )
    
    # Application Insights (optional)
    applicationinsights_connection_string: str = Field(
        default="",
        alias="APPLICATIONINSIGHTS_CONNECTION_STRING",
        description="Application Insights connection string for telemetry"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()
