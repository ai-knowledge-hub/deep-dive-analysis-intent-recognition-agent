"""
LLM Provider - Unified interface for Claude and GPT-4.

This module provides a clean abstraction over different LLM providers,
allowing easy switching between Anthropic Claude and OpenAI GPT-4.
"""

import os
import json
from typing import Dict, Any, Optional, Literal, List, Sequence
from abc import ABC, abstractmethod

import requests

try:
    from anthropic import Anthropic as AnthropicClient
    ANTHROPIC_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    AnthropicClient = None  # type: ignore[assignment]
    ANTHROPIC_AVAILABLE = False

try:
    from openai import OpenAI as OpenAIClient
    OPENAI_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    OpenAIClient = None  # type: ignore[assignment]
    OPENAI_AVAILABLE = False


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    def generate_sync(self, prompt: str, system_prompt: str = "") -> str:
        """Synchronous version of generate."""
        pass


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.3
    ):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model name
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (lower = more deterministic)
        """
        if not ANTHROPIC_AVAILABLE or AnthropicClient is None:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")

        self.client = AnthropicClient(api_key=self.api_key)
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate_sync(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response synchronously."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt if system_prompt else "You are a helpful AI assistant.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content_blocks: Sequence[Any] = getattr(message, "content", [])
            if not content_blocks:
                raise RuntimeError("Anthropic API error: empty content")

            first_block = content_blocks[0]
            text = getattr(first_block, "text", None)
            if text is None:
                raise RuntimeError("Anthropic API error: no text in content block")

            return str(text)

        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Async version (currently wraps sync)."""
        # For now, use sync version
        # TODO: Use async client when available
        return self.generate_sync(prompt, system_prompt)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.3
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        """
        if not OPENAI_AVAILABLE or OpenAIClient is None:
            raise ImportError("openai package not installed. Run: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

        self.client = OpenAIClient(api_key=self.api_key)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate_sync(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response synchronously."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt if system_prompt else "You are a helpful AI assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            message = response.choices[0].message
            content = getattr(message, "content", None)
            if content is None:
                raise RuntimeError("OpenAI API error: empty response content")
            return str(content)

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Async version (currently wraps sync)."""
        # For now, use sync version
        # TODO: Use async client when available
        return self.generate_sync(prompt, system_prompt)


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter proxy provider using the HTTP API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.3,
        base_url: str = "https://openrouter.ai/api/v1",
        referer: Optional[str] = None,
        site_title: Optional[str] = None,
    ):
        if not api_key:
            api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OpenRouter API key not provided")

        self.api_key = api_key
        self.model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.base_url = base_url.rstrip("/")
        self.referer = referer or os.getenv("OPENROUTER_SITE_URL")
        self.site_title = site_title or os.getenv("OPENROUTER_SITE_NAME")

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.referer:
            headers["HTTP-Referer"] = self.referer
        if self.site_title:
            headers["X-Title"] = self.site_title
        return headers

    def _build_payload(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        messages: List[Dict[str, str]] = []  # type: ignore[name-defined]
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

    def generate_sync(self, prompt: str, system_prompt: str = "") -> str:
        payload = self._build_payload(prompt, system_prompt)
        url = f"{self.base_url}/chat/completions"

        response = requests.post(url, headers=self._headers(), data=json.dumps(payload), timeout=60)
        if response.status_code != 200:
            try:
                error_payload = response.json()
                message = error_payload.get("error", {}).get("message", response.text)
            except Exception:  # noqa: BLE001
                message = response.text
            raise RuntimeError(f"OpenRouter API error: {message}")

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:  # noqa: BLE001
            raise RuntimeError(f"Unexpected OpenRouter response: {data}") from exc

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        return self.generate_sync(prompt, system_prompt)


class LLMProviderFactory:
    """Factory for creating LLM providers."""

    @staticmethod
    def create(
        provider_name: Literal["anthropic", "openai", "openrouter"] = "anthropic",
        **kwargs
    ) -> BaseLLMProvider:
        """
        Create an LLM provider.

        Args:
            provider_name: "anthropic" or "openai"
            **kwargs: Provider-specific arguments

        Returns:
            LLM provider instance
        """
        if provider_name == "anthropic":
            return AnthropicProvider(**kwargs)
        elif provider_name == "openai":
            return OpenAIProvider(**kwargs)
        elif provider_name == "openrouter":
            return OpenRouterProvider(**kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

    @staticmethod
    def create_from_env() -> BaseLLMProvider:
        """
        Create provider based on environment variables.

        Checks for ANTHROPIC_API_KEY first, then OPENAI_API_KEY.

        Returns:
            LLM provider instance
        """
        if os.getenv("ANTHROPIC_API_KEY"):
            return AnthropicProvider()
        if os.getenv("OPENAI_API_KEY"):
            return OpenAIProvider()
        if os.getenv("OPENROUTER_API_KEY"):
            return OpenRouterProvider()
        else:
            raise ValueError(
                "No API key found in environment. Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY"
            )
