"""
Factory pattern for AWS Bedrock clients.
Provides singleton instances of BedrockEmbeddings and ChatBedrock.
"""
import boto3
from functools import lru_cache
from langchain_aws import BedrockEmbeddings, ChatBedrock
from Src.Config.config import get_settings

settings = get_settings()


@lru_cache
def get_bedrock_client():
    """Singleton boto3 bedrock-runtime client."""
    kwargs = {
        "region_name": settings.aws_region,
        "aws_access_key_id": settings.aws_access_key_id,
        "aws_secret_access_key": settings.aws_secret_access_key,
    }
    if settings.aws_session_token:
        kwargs["aws_session_token"] = settings.aws_session_token
    return boto3.client("bedrock-runtime", **kwargs)


@lru_cache
def get_embedding_model() -> BedrockEmbeddings:
    """Factory: returns singleton BedrockEmbeddings (Titan v2)."""
    return BedrockEmbeddings(
        client=get_bedrock_client(),
        model_id=settings.bedrock_embedding_model_id,
    )


@lru_cache
def get_llm() -> ChatBedrock:
    """Factory: returns singleton ChatBedrock (Claude Haiku)."""
    return ChatBedrock(
        client=get_bedrock_client(),
        model_id=settings.bedrock_llm_model_id,
        model_kwargs={"max_tokens": 1024, "temperature": 0.2},
    )
