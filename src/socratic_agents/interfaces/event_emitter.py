"""Event emitter service interface - abstraction for event system."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional


class EventEmitterService(ABC):
    """Abstract interface for event emission and handling."""

    @abstractmethod
    async def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event synchronously."""
        pass

    @abstractmethod
    async def emit_async(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event asynchronously (non-blocking)."""
        pass

    @abstractmethod
    def on(self, event_type: str, handler: Callable) -> None:
        """Register event listener."""
        pass

    @abstractmethod
    def off(self, event_type: str, handler: Callable) -> None:
        """Unregister event listener."""
        pass

    @abstractmethod
    def once(self, event_type: str, handler: Callable) -> None:
        """Register one-time event listener."""
        pass

    @abstractmethod
    async def wait_for(self, event_type: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Wait for an event to be emitted."""
        pass
