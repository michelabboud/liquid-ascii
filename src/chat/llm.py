"""
LLM backend interface and implementations.

Supports multiple LLM providers:
- Ollama (local models)
- OpenAI API
- Extensible for other providers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, AsyncIterator
import json
import asyncio
import aiohttp


class LLMBackend(ABC):
    """Abstract base class for LLM backends."""

    @abstractmethod
    async def generate(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500
    ) -> str:
        """
        Generate a response from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response text
        """
        pass

    @abstractmethod
    async def stream_generate(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500
    ) -> AsyncIterator[str]:
        """
        Stream response tokens from the LLM.

        Args:
            messages: List of message dicts
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Response tokens as they're generated
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available."""
        pass


class OllamaBackend(LLMBackend):
    """
    Ollama backend for local LLM inference.

    Requires Ollama to be installed and running.
    """

    def __init__(
        self, model: str = "llama3.2:latest", base_url: str = "http://localhost:11434"
    ):
        """
        Initialize Ollama backend.

        Args:
            model: Model name (e.g., "llama3.2:latest", "mistral", "phi")
            base_url: Ollama API base URL
        """
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api"

    async def generate(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500
    ) -> str:
        """Generate response using Ollama."""
        url = f"{self.api_url}/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["message"]["content"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error: {response.status} - {error_text}")
            except asyncio.TimeoutError:
                raise Exception("Ollama request timed out")
            except aiohttp.ClientConnectorError:
                raise Exception("Cannot connect to Ollama. Is it running?")

    async def stream_generate(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500
    ) -> AsyncIterator[str]:
        """Stream response using Ollama."""
        url = f"{self.api_url}/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error: {response.status} - {error_text}")

                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode("utf-8"))
                                if "message" in data and "content" in data["message"]:
                                    content = data["message"]["content"]
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
            except aiohttp.ClientConnectorError:
                raise Exception("Cannot connect to Ollama. Is it running?")

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        import requests

        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return False


class OpenAIBackend(LLMBackend):
    """
    OpenAI API backend.

    Requires OpenAI API key in environment variable OPENAI_API_KEY.
    """

    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        """
        Initialize OpenAI backend.

        Args:
            model: Model name (e.g., "gpt-4o-mini", "gpt-4o", "gpt-4-turbo")
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        """
        import os

        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        self.base_url = "https://api.openai.com/v1"

    async def generate(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500
    ) -> str:
        """Generate response using OpenAI API."""
        url = f"{self.base_url}/chat/completions"

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"OpenAI API error: {response.status} - {error_text}")
            except asyncio.TimeoutError:
                raise Exception("OpenAI request timed out")

    async def stream_generate(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500
    ) -> AsyncIterator[str]:
        """Stream response using OpenAI API."""
        url = f"{self.base_url}/chat/completions"

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error: {response.status} - {error_text}")

                async for line in response.content:
                    if line:
                        line_text = line.decode("utf-8").strip()
                        if line_text.startswith("data: "):
                            data_text = line_text[6:]  # Remove "data: " prefix
                            if data_text == "[DONE]":
                                break
                            try:
                                data = json.loads(data_text)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue

    def is_available(self) -> bool:
        """Check if OpenAI API is configured."""
        return self.api_key is not None


def create_llm_backend(backend_type: str = "ollama", **kwargs) -> LLMBackend:
    """
    Factory function to create LLM backend.

    Args:
        backend_type: Type of backend ("ollama" or "openai")
        **kwargs: Additional arguments for backend initialization

    Returns:
        LLMBackend instance

    Raises:
        ValueError: If backend type is unknown
    """
    if backend_type == "ollama":
        return OllamaBackend(**kwargs)
    elif backend_type == "openai":
        return OpenAIBackend(**kwargs)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")


def list_available_backends() -> List[str]:
    """
    List currently available backends.

    Returns:
        List of available backend names
    """
    available = []

    # Check Ollama
    try:
        ollama = OllamaBackend()
        if ollama.is_available():
            available.append("ollama")
    except Exception:
        pass

    # Check OpenAI
    try:
        import os

        if os.environ.get("OPENAI_API_KEY"):
            available.append("openai")
    except Exception:
        pass

    return available
