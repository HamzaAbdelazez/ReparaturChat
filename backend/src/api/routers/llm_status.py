"""
LLM Status Router
Provides information about available LLM providers
"""

from fastapi import APIRouter
from api.service.llm_service import llm_service, LLMProvider

router = APIRouter(prefix="/llm", tags=["llm"])

@router.get("/status")
def get_llm_status():
    """Get the status of all LLM providers."""
    available_providers = llm_service.get_available_providers()
    
    return {
        "available_providers": [provider.value for provider in available_providers],
        "provider_details": {
            "gemma3": {
                "available": llm_service.is_provider_available(LLMProvider.GEMMA3),
                "description": "Fast and reliable via Replicate",
                "icon": "zap"
            },
            "gemini": {
                "available": llm_service.is_provider_available(LLMProvider.GEMINI),
                "description": "Advanced reasoning by Google",
                "icon": "brain"
            },
            "deepseek": {
                "available": llm_service.is_provider_available(LLMProvider.DEEPSEEK),
                "description": "Advanced reasoning model via Replicate",
                "icon": "cpu"
            },
            "gpt5": {
                "available": llm_service.is_provider_available(LLMProvider.GPT5),
                "description": "Latest OpenAI model via Replicate",
                "icon": "sparkles"
            }
        }
    }