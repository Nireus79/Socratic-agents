"""Agent communication bus for inter-agent message routing."""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set


class MessageType(str, Enum):
    """Types of messages that can be sent between agents."""

    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    QUERY = "query"
    COMMAND = "command"
    ERROR = "error"


@dataclass
class AgentMessage:
    """Message sent between agents."""

    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType = MessageType.REQUEST
    from_agent: str = ""
    to_agent: str = ""
    action: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    reply_to: Optional[str] = None
    priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "action": self.action,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "reply_to": self.reply_to,
            "priority": self.priority,
        }


class AgentBus:
    """Central message bus for agent communication."""

    def __init__(self, enable_persistence: bool = False):
        """Initialize agent bus."""
        self.logger = logging.getLogger("socratic_agents.bus")
        self.enable_persistence = enable_persistence
        self._agents: Dict[str, Any] = {}
        self._subscriptions: Dict[MessageType, List[Callable]] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._message_history: List[AgentMessage] = []
        self._max_history = 1000

    def register_agent(self, agent_id: str, agent: Any) -> None:
        """Register an agent on the bus."""
        self._agents[agent_id] = agent
        self.logger.info(f"Registered agent on bus: {agent_id}")

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the bus."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            self.logger.info(f"Unregistered agent from bus: {agent_id}")

    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get agent by ID."""
        return self._agents.get(agent_id)

    def list_agents(self) -> List[str]:
        """List all registered agents."""
        return list(self._agents.keys())

    async def send_message(
        self,
        message: AgentMessage,
        wait_for_response: bool = False,
        timeout: float = 30.0,
    ) -> Optional[AgentMessage]:
        """Send a message from one agent to another."""
        self.logger.info(
            f"Message {message.message_id} from {message.from_agent} "
            f"to {message.to_agent}: {message.action}"
        )

        self._message_history.append(message)
        if len(self._message_history) > self._max_history:
            self._message_history = self._message_history[-self._max_history :]

        await self._message_queue.put(message)

        target_agent = self.get_agent(message.to_agent)
        if target_agent:
            await self._route_message(message, target_agent)

        await self._emit_to_subscribers(message)
        return None

    async def broadcast_message(
        self,
        message: AgentMessage,
        exclude_agents: Optional[Set[str]] = None,
    ) -> int:
        """Broadcast a message to all agents."""
        exclude_agents = exclude_agents or set()
        notified = 0

        for agent_id in self.list_agents():
            if agent_id not in exclude_agents:
                message.to_agent = agent_id
                await self.send_message(message)
                notified += 1

        return notified

    async def _route_message(
        self,
        message: AgentMessage,
        target_agent: Any,
    ) -> None:
        """Route message to target agent."""
        try:
            if hasattr(target_agent, "on_message"):
                await target_agent.on_message(message)
            elif hasattr(target_agent, "receive_message"):
                await target_agent.receive_message(message)
        except Exception as e:
            self.logger.error(f"Error routing message {message.message_id}: {e}")

    async def _emit_to_subscribers(self, message: AgentMessage) -> None:
        """Emit message to subscribers of that message type."""
        subscribers = self._subscriptions.get(message.message_type, [])
        for subscriber in subscribers:
            try:
                await subscriber(message)
            except Exception as e:
                self.logger.error(f"Error in subscriber for {message.message_type}: {e}")

    def subscribe(
        self,
        message_type: MessageType,
        callback: Callable[[AgentMessage], Any],
    ) -> None:
        """Subscribe to messages of a specific type."""
        if message_type not in self._subscriptions:
            self._subscriptions[message_type] = []
        self._subscriptions[message_type].append(callback)
        self.logger.info(f"Added subscriber for {message_type.value}")

    def unsubscribe(
        self,
        message_type: MessageType,
        callback: Callable,
    ) -> None:
        """Unsubscribe from message type."""
        if message_type in self._subscriptions:
            if callback in self._subscriptions[message_type]:
                self._subscriptions[message_type].remove(callback)

    def get_message_history(
        self,
        from_agent: Optional[str] = None,
        to_agent: Optional[str] = None,
        limit: int = 100,
    ) -> List[AgentMessage]:
        """Get message history with optional filtering."""
        results = self._message_history

        if from_agent:
            results = [m for m in results if m.from_agent == from_agent]
        if to_agent:
            results = [m for m in results if m.to_agent == to_agent]

        return results[-limit:]

    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get message statistics for an agent."""
        sent = len([m for m in self._message_history if m.from_agent == agent_id])
        received = len([m for m in self._message_history if m.to_agent == agent_id])

        return {
            "agent_id": agent_id,
            "messages_sent": sent,
            "messages_received": received,
            "total_messages": sent + received,
        }
