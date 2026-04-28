"""Provider contracts for durable memory and learning events."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseMemoryProvider(ABC):
    """Abstract storage backend for memory files, entries, and learning events."""

    @abstractmethod
    def read_user(self) -> str: ...

    @abstractmethod
    def write_user(self, content: str) -> None: ...

    @abstractmethod
    def read_soul(self) -> str: ...

    @abstractmethod
    def write_soul(self, content: str) -> None: ...

    @abstractmethod
    def read_memory(self) -> str: ...

    @abstractmethod
    def write_memory(self, content: str) -> None: ...

    @abstractmethod
    def add_entry(self, target: str, content: str, metadata: dict[str, Any] | None = None) -> str: ...

    @abstractmethod
    def replace_entry(self, target: str, old_text: str, new_text: str) -> None: ...

    @abstractmethod
    def remove_entry(self, target: str, old_text: str) -> None: ...

    @abstractmethod
    def search_memory(self, query: str, limit: int = 8) -> list[dict[str, Any]]: ...

    @abstractmethod
    def append_learning_event(self, event: dict[str, Any]) -> str: ...

    @abstractmethod
    def read_learning_events(self, status: str = "pending", limit: int = 50) -> list[dict[str, Any]]: ...

    @abstractmethod
    def update_learning_event(self, event_id: str, status: str, reason: str | None = None) -> None: ...
