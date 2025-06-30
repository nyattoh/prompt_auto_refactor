"""Anthropic API client implementation"""
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
import anthropic
from anthropic import Anthropic, APIError


@dataclass
class APIResponse:
    """Response from API calls"""
    content: str
    model: str
    usage: Dict[str, int]
    status: Optional[str] = None


class AnthropicClient:
    """Client for interacting with Anthropic API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Anthropic client
        
        Args:
            api_key: API key for Anthropic. If not provided, reads from ANTHROPIC_API_KEY env var
            
        Raises:
            ValueError: If no API key is found
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please provide api_key or set ANTHROPIC_API_KEY")
        
        # Default configuration
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        self.max_tokens = int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096"))
        
        # Initialize the Anthropic client
        self.client = Anthropic(api_key=self.api_key)
    
    def test_connection(self) -> APIResponse:
        """Test connection to Anthropic API
        
        Returns:
            APIResponse with status "connected" if successful
        """
        try:
            # Send a minimal test message
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[
                    {"role": "user", "content": "Say 'OK' if you can hear me"}
                ]
            )
            
            return APIResponse(
                content=response.content[0].text,
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
                status="connected"
            )
        except APIError as e:
            return APIResponse(
                content=f"Connection failed: {str(e)}",
                model=self.model,
                usage={"input_tokens": 0, "output_tokens": 0},
                status="error"
            )
    
    def execute_prompt(self, prompt: str, system_prompt: Optional[str] = None) -> APIResponse:
        """Execute a prompt and get response
        
        Args:
            prompt: The prompt to send to the API
            system_prompt: Optional system prompt to set context
            
        Returns:
            APIResponse containing the response
        """
        # Use internal API call method
        return self._call_api(prompt, system_prompt)
    
    def _call_api(self, prompt: str, system_prompt: Optional[str] = None) -> APIResponse:
        """Internal method to call Anthropic API
        
        Args:
            prompt: The prompt to send
            system_prompt: Optional system prompt
            
        Returns:
            APIResponse from the API
        """
        try:
            # Build messages
            messages = [{"role": "user", "content": prompt}]
            
            # Create the API request
            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": messages
            }
            
            # Add system prompt if provided
            if system_prompt:
                kwargs["system"] = system_prompt
            
            # Make the API call
            response = self.client.messages.create(**kwargs)
            
            # Extract content from response
            content = response.content[0].text if response.content else ""
            
            return APIResponse(
                content=content,
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            )
            
        except Exception as e:
            # Handle API errors gracefully
            return APIResponse(
                content=f"API Error: {str(e)}",
                model=self.model,
                usage={"input_tokens": 0, "output_tokens": 0},
                status="error"
            ) 