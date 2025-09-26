"""Simple caching helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.config import get_settings


@dataclass
class MemoryCache:
    data: Dict[str, Any]

    def __init__(self) -> None:
        self.data = {}

    def get(self, key: str) -> Any:
        return self.data.get(key)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value


class CacheFactory:
    """Factory constructing cache instances based on configuration."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def create(self) -> MemoryCache:
        # Redis integration can be added later; we default to in-memory cache.
        return MemoryCache()


__all__ = ["CacheFactory", "MemoryCache"]
