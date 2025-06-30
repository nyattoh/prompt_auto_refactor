"""Tests for Anthropic API client"""
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# This import will fail initially (Red phase)
from src.llm.anthropic_client import AnthropicClient, APIResponse


class TestAnthropicClient:
    """Test suite for Anthropic API client"""

    def test_anthropic_client_initialization(self):
        """APIキーでクライアントを初期化できる"""
        client = AnthropicClient(api_key="test-key")
        assert client.api_key == "test-key"

    def test_anthropic_client_initialization_from_env(self):
        """環境変数からAPIキーを読み込める"""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-test-key"}):
            client = AnthropicClient()
            assert client.api_key == "env-test-key"

    def test_anthropic_client_no_api_key_raises(self):
        """APIキーがない場合はエラーを発生させる"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key not found"):
                AnthropicClient()

    @patch('src.llm.anthropic_client.Anthropic')
    def test_anthropic_client_connection_mock(self, mock_anthropic_class):
        """APIへの接続をモックでテスト"""
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        
        # Mock response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="OK")]
        mock_response.model = "claude-3-sonnet-20240229"
        mock_response.usage.input_tokens = 5
        mock_response.usage.output_tokens = 1
        
        mock_client.messages.create.return_value = mock_response
        
        # Test
        client = AnthropicClient(api_key="test-key")
        response = client.test_connection()
        
        assert response.status == "connected"
        assert response.content == "OK"
        assert response.usage["input_tokens"] == 5
        assert response.usage["output_tokens"] == 1

    @patch('src.llm.anthropic_client.Anthropic')
    def test_anthropic_prompt_execution_mock(self, mock_anthropic_class):
        """プロンプト実行のモックテスト"""
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        
        # Mock response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Hello! I'm Claude.")]
        mock_response.model = "claude-3-sonnet-20240229"
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 20
        
        mock_client.messages.create.return_value = mock_response
        
        # Test
        client = AnthropicClient(api_key="test-key")
        response = client.execute_prompt("Hello, Claude")
        
        assert response.content == "Hello! I'm Claude."
        assert response.model == "claude-3-sonnet-20240229"
        assert response.usage["input_tokens"] == 10
        assert response.usage["output_tokens"] == 20
        
        # Verify API was called correctly
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args[1]
        assert call_args["messages"] == [{"role": "user", "content": "Hello, Claude"}]
        assert call_args["model"] == "claude-3-sonnet-20240229"

    @patch('src.llm.anthropic_client.Anthropic')
    def test_anthropic_system_prompt(self, mock_anthropic_class):
        """システムプロンプトを含むプロンプト実行のテスト"""
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        
        # Mock response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="I understand.")]
        mock_response.model = "claude-3-sonnet-20240229"
        mock_response.usage.input_tokens = 15
        mock_response.usage.output_tokens = 5
        
        mock_client.messages.create.return_value = mock_response
        
        # Test
        client = AnthropicClient(api_key="test-key")
        response = client.execute_prompt(
            "What's your role?",
            system_prompt="You are a helpful assistant."
        )
        
        assert response.content == "I understand."
        
        # Verify system prompt was passed
        call_args = mock_client.messages.create.call_args[1]
        assert call_args["system"] == "You are a helpful assistant."

    @patch('src.llm.anthropic_client.Anthropic')
    def test_anthropic_api_error_handling(self, mock_anthropic_class):
        """APIエラーのハンドリングテスト"""
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        
        # Mock API error - use generic Exception instead of APIError
        mock_client.messages.create.side_effect = Exception("Rate limit exceeded")
        
        # Test
        client = AnthropicClient(api_key="test-key")
        response = client.execute_prompt("Hello")
        
        assert "API Error" in response.content
        assert "Rate limit exceeded" in response.content
        assert response.status == "error"
        assert response.usage["input_tokens"] == 0
        assert response.usage["output_tokens"] == 0

    @pytest.mark.llm
    def test_anthropic_client_connection(self):
        """APIへの接続をテストできる (実際のAPI使用)"""
        # Skip if no API key
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")
            
        client = AnthropicClient()
        response = client.test_connection()
        assert response.status == "connected"
        assert len(response.content) > 0

    @pytest.mark.llm
    def test_anthropic_prompt_execution(self):
        """プロンプトを実行して応答を得られる (実際のAPI使用)"""
        # Skip if no API key
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")
            
        client = AnthropicClient()
        response = client.execute_prompt("Say 'Hello, test!' and nothing else.")
        assert len(response.content) > 0
        assert response.model is not None
        assert response.usage is not None
        assert response.usage["input_tokens"] > 0
        assert response.usage["output_tokens"] > 0 