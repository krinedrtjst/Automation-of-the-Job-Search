"""Native CrewAI Bedrock integration for the synchronous application pipeline."""

import logging
import os
from typing import Any, Dict, Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from crewai.llms.providers.bedrock.completion import BedrockCompletion

logger = logging.getLogger(__name__)

TRANSIENT_ERRORS = {
    "ThrottlingException", 
    "ServiceUnavailableException",
    "InternalServerException", 
    "ModelNotReadyException",
}


class FallbackClient:
    """Retry only a failed API request, never replay already executed tools."""

    def __init__(self, client: Any, fallback_model: Optional[str]):
        self.client = client
        self.fallback_model = fallback_model

    def converse(self, **request: Any) -> Dict[str, Any]:
        try:
            return self.client.converse(**request)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            
            # Raise immediately if error is not transient or no fallback exists
            if code not in TRANSIENT_ERRORS or not self.fallback_model:
                raise
                
            # Raise if we are already using the fallback model and it failed
            if request.get("modelId") == self.fallback_model:
                raise
                
            logger.warning(
                "Bedrock %s: switching from %s to %s", 
                code,
                request.get("modelId"), 
                self.fallback_model
            )
            
            # Update request to use the fallback model and retry
            request["modelId"] = self.fallback_model
            return self.client.converse(**request)


class ProjectBedrockLLM(BedrockCompletion):
    """Custom Bedrock LLM wrapper with strict IAM profile enforcement and fallbacks."""
    
    fallback_model: Optional[str] = None

    def _build_sync_client(self) -> FallbackClient:
        # Explicit profile prevents unrelated environment credentials from taking
        # precedence over the project's restricted IAM identity.
        profile = os.getenv("AWS_PROFILE")
        if not profile:
            raise ValueError("Configure AWS_PROFILE for local Bedrock access")
            
        session = boto3.Session(profile_name=profile, region_name=self.region_name)
        client = session.client(
            "bedrock-runtime", 
            config=Config(
                read_timeout=300, 
                connect_timeout=10,
                retries={"max_attempts": 3, "mode": "standard"},
            )
        )
        return FallbackClient(client, self.fallback_model)

    async def acall(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Use synchronous call() for the local Bedrock pipeline")