import os
import logging
from typing import Optional, Any
from dotenv import load_dotenv

# Initialize logging for the factory
logger = logging.getLogger(__name__)

load_dotenv()

_MODELS = {
    "openai":    "openai/gpt-4o",
    "anthropic": "anthropic/claude-3-5-sonnet-latest",  # Updated to canonical Claude 3.5 Sonnet
    "gemini":    "gemini/gemini-1.5-pro",               # Updated to canonical Gemini 1.5 Pro
    "grok":      "xai/grok-2-latest",                   # Updated to canonical Grok 2
}

_API_KEY_ENV = {
    "openai":    "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini":    "GOOGLE_API_KEY",
    "grok":      "XAI_API_KEY",
}


def get_llm(provider: Optional[str] = None, temperature: float = 0.2, purpose: str = "main") -> Any:
    """
    Returns a crewai.LLM instance for the given provider.
    Default temperature is set to 0.2 to heavily penalize hallucinations during resume parsing.
    """
    try:
        from crewai import LLM
    except ImportError as e:
        logger.error("Failed to import crewai.LLM. Ensure crewai is installed.")
        raise e

    provider = (provider or os.getenv("LLM_PROVIDER", "openai")).lower().strip()
    
    # ─── BEDROCK HANDLING ──────────────────────────────────────────────────────
    if provider == "bedrock":
        try:
            from src.bedrock_llm import ProjectBedrockLLM
        except ImportError as e:
            logger.error("Failed to import ProjectBedrockLLM from src.bedrock_llm")
            raise e

        extraction = (purpose == "extraction")
        
        # Determine main model
        raw_model = os.getenv(
            "BEDROCK_EXTRACTION_MODEL_ID" if extraction else "BEDROCK_MODEL_ID",
            "deepseek.v3.2" if extraction else "us.anthropic.claude-3-5-sonnet-latest"
        )
        model = raw_model.replace("bedrock/", "", 1).strip()
        
        if not model or not os.getenv("AWS_PROFILE"):
            raise ValueError("Bedrock integration requires an AWS_PROFILE and a nonempty model ID in your .env")
            
        # Determine fallback model
        raw_fallback = os.getenv(
            "BEDROCK_FALLBACK_MODEL_ID", 
            "us.anthropic.claude-3-5-sonnet-latest"
        )
        fallback = raw_fallback.replace("bedrock/", "", 1).strip()
        fallback_model = None if extraction else (fallback or None)
        
        # Max tokens validation
        try:
            max_tokens = int(os.getenv("BEDROCK_MAX_TOKENS", "16384"))
            if max_tokens <= 0:
                raise ValueError
        except ValueError:
            raise ValueError("BEDROCK_MAX_TOKENS must be a positive integer")
            
        return ProjectBedrockLLM(
            model=model, 
            fallback_model=fallback_model,
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            temperature=temperature, 
            max_tokens=max_tokens, 
            stream=False,
        )

    # ─── STANDARD PROVIDERS (OpenAI, Anthropic, Gemini, Grok) ──────────────────
    model = _MODELS.get(provider)
    if not model:
        raise ValueError(
            f"Provider not supported: '{provider}'. "
            f"Choose from: {', '.join(_MODELS.keys())}, bedrock"
        )
        
    api_key_env_var = _API_KEY_ENV.get(provider, "")
    api_key = os.getenv(api_key_env_var)
    
    if not api_key:
        logger.warning(f"No API key found for provider '{provider}' (expected {api_key_env_var} in .env)")

    kwargs = {"temperature": temperature}
    if api_key:
        kwargs["api_key"] = api_key
        
    if provider == "grok":
        # xAI's API rejects the "stop" param CrewAI sends by default,
        # and CrewAI's automatic retry-without-stop only matches OpenAI-style 
        # error phrasing. Drop it up front.
        kwargs["additional_params"] = {"additional_drop_params": ["stop"]}
        
    return LLM(model=model, **kwargs)