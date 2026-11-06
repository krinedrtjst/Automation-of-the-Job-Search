import os
import unittest
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError

# Ensure these imports point to your actual project structure
from src.bedrock_llm import FallbackClient, ProjectBedrockLLM
from src.llm_factory import get_llm


def generate_aws_error(code: str) -> ClientError:
    """Helper function to mock AWS Boto3 ClientErrors."""
    return ClientError({"Error": {"Code": code, "Message": "test exception"}}, "Converse")


class BedrockTests(unittest.TestCase):
    """Test suite for the Bedrock LLM integration, fallbacks, and factory routing."""

    def test_fallback_preserves_tool_history(self):
        """
        Ensures that when a transient error occurs (e.g., Throttling), 
        the FallbackClient correctly swaps the modelId without dropping the 
        tool execution history.
        """
        client = Mock()
        # First call fails, second succeeds
        client.converse.side_effect = [generate_aws_error("ThrottlingException"), {"output": "ok"}]
        
        request = {
            "modelId": "us.anthropic.claude-3-opus-20240229-v1:0", 
            "messages": [{"role": "user", "content": [
                {"toolResult": {"toolUseId": "saved", "content": [{"text": "saved"}]}}
            ]}], 
            "toolConfig": {"tools": []}
        }
        
        fallback_model = "us.anthropic.claude-3-5-sonnet-latest"
        
        # Test the response
        response = FallbackClient(client, fallback_model).converse(**request)
        self.assertEqual(response, {"output": "ok"})
        
        # Test that the second call to the underlying client used the fallback model
        expected_kwargs = request.copy()
        expected_kwargs["modelId"] = fallback_model
        self.assertEqual(client.converse.call_args.kwargs, expected_kwargs)
        
        # Test that the original request dictionary was NOT mutated
        self.assertEqual(request["modelId"], "us.anthropic.claude-3-opus-20240229-v1:0")

    def test_permanent_errors_do_not_fallback(self):
        """
        Ensures that permanent errors (e.g., AccessDenied) fail immediately
        without attempting to hit the fallback model.
        """
        permanent_codes = ["AccessDeniedException", "ValidationException", "ResourceNotFoundException"]
        
        for code in permanent_codes:
            with self.subTest(code=code):
                client = Mock()
                client.converse.side_effect = generate_aws_error(code)
                
                with self.assertRaises(ClientError):
                    FallbackClient(client, "us.anthropic.claude-3-5-sonnet-latest").converse(modelId="opus")
                
                # Should only be called once; no fallback attempt
                self.assertEqual(client.converse.call_count, 1)

    def test_fallback_failure_propagates_once(self):
        """
        If the fallback model ALSO throws a transient error, the exception 
        should propagate rather than causing an infinite loop.
        """
        client = Mock()
        # Both the original and fallback calls fail
        client.converse.side_effect = generate_aws_error("ServiceUnavailableException")
        
        with self.assertRaises(ClientError):
            FallbackClient(client, "us.anthropic.claude-3-5-sonnet-latest").converse(modelId="opus")
            
        # Original call + Fallback call = 2
        self.assertEqual(client.converse.call_count, 2)

    def test_no_fallback_for_extraction(self):
        """
        Ensures that if no fallback_model is provided (e.g., during strict extraction),
        a transient error fails immediately.
        """
        client = Mock()
        client.converse.side_effect = generate_aws_error("ThrottlingException")
        
        with self.assertRaises(ClientError):
            FallbackClient(client, fallback_model=None).converse(modelId="deepseek.v3.2")
            
        self.assertEqual(client.converse.call_count, 1)

    @patch.object(ProjectBedrockLLM, "_build_sync_client", return_value=Mock())
    def test_factory_routes_and_preserves_tool_support(self, mock_build):
        """
        Tests that `get_llm("bedrock")` correctly sets up the models, 
        flags, and fallbacks for both 'main' and 'extraction' purposes.
        """
        env_vars = {
            "AWS_PROFILE": "test",
            "BEDROCK_MODEL_ID": "us.anthropic.claude-3-opus-20240229-v1:0",
            "BEDROCK_FALLBACK_MODEL_ID": "us.anthropic.claude-3-5-sonnet-latest",
            "BEDROCK_EXTRACTION_MODEL_ID": "deepseek.v3.2"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            main_llm = get_llm("bedrock")
            extraction_llm = get_llm("bedrock", purpose="extraction")
            
            # Assertions for Main LLM
            self.assertEqual(main_llm.model_id, "us.anthropic.claude-3-opus-20240229-v1:0")
            self.assertEqual(main_llm.fallback_model, "us.anthropic.claude-3-5-sonnet-latest")
            self.assertTrue(main_llm.supports_function_calling())
            self.assertFalse(main_llm.stream)
            
            # Assertions for Extraction LLM
            self.assertEqual(extraction_llm.model_id, "deepseek.v3.2")
            self.assertIsNone(extraction_llm.fallback_model)

    def test_missing_profile_fails(self):
        """
        Ensures that initializing the Bedrock LLM without an AWS_PROFILE 
        raises a clear, informative ValueError.
        """
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "AWS_PROFILE"):
                get_llm("bedrock")

    @patch("src.bedrock_llm.boto3.Session")
    def test_explicit_profile_is_used(self, mock_session):
        """
        Ensures that the boto3 Session explicitly uses the restricted profile
        defined in the .env file.
        """
        with patch.dict(os.environ, {"AWS_PROFILE": "restricted"}):
            get_llm("bedrock")
            
        mock_session.assert_called_once_with(profile_name="restricted", region_name="us-east-1")


if __name__ == "__main__":
    unittest.main()