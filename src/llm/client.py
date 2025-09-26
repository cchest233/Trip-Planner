"""LangChain LLM client selection utilities."""
from __future__ import annotations

import os
from typing import Any, Dict

from langchain.llms.base import LLM
from langchain.schema import LLMResult

from src.config import get_settings


class DemoLLM(LLM):
    """Deterministic LLM returning templated narration for demos."""

    @property
    def _llm_type(self) -> str:
        return "demo"

    def _call(self, prompt: str, stop: list[str] | None = None) -> str:
        return (
            "This is a sample narration summarizing the proposed itinerary. "
            "Explore highlights, enjoy local cuisine, and stay flexible."
        )

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"provider": "demo"}

    async def _acall(self, prompt: str, stop: list[str] | None = None) -> str:
        return self._call(prompt, stop)

    def generate(self, prompts: list[str], **kwargs: Any) -> LLMResult:  # type: ignore[override]
        generations = [[self._call(prompt)] for prompt in prompts]
        return LLMResult(generations=[[{"text": text} for text in batch] for batch in generations])


class UnsupportedProviderError(RuntimeError):
    """Raised when the configured LLM provider is not implemented."""


def get_llm() -> LLM:
    """Return an instantiated LangChain LLM based on environment configuration."""

    settings = get_settings()
    provider = settings.llm_provider.lower()
    if provider == "demo":
        return DemoLLM()

    if provider in {"openai", "anthropic", "google"}:
        # Stub implementations for future integration. We avoid importing SDKs
        # until API keys are supplied to keep the minimal repo runnable.
        api_key_env = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
        }[provider]
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise UnsupportedProviderError(
                f"Provider '{provider}' requires environment variable '{api_key_env}'."
            )
        raise UnsupportedProviderError(
            f"Provider '{provider}' integration not yet implemented."
        )

    raise UnsupportedProviderError(f"Unknown LLM provider '{settings.llm_provider}'.")


__all__ = ["get_llm", "DemoLLM", "UnsupportedProviderError"]
