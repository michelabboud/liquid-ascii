"""
Conversation memory system for chat mode.

Manages chat history, context window, and memory persistence.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    """A single message in the conversation."""

    role: str  # "user", "assistant", or "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """Create from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


class ConversationMemory:
    """
    Manages conversation history and context.

    Features:
    - Stores message history
    - Manages context window (token limits)
    - Provides sliding window of recent messages
    - Supports saving/loading conversations
    """

    def __init__(self, max_messages: int = 50, context_window: int = 20):
        """
        Initialize conversation memory.

        Args:
            max_messages: Maximum messages to store (unlimited if -1)
            context_window: Number of recent messages to include in context
        """
        self.max_messages = max_messages
        self.context_window = context_window
        self.messages: list[Message] = []
        self.system_message: Message | None = None

    def set_system_message(self, content: str):
        """Set or update the system message."""
        self.system_message = Message(role="system", content=content)

    def add_message(self, role: str, content: str, metadata: dict | None = None):
        """
        Add a message to conversation history.

        Args:
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Optional metadata
        """
        message = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(message)

        # Trim if exceeding max messages
        if self.max_messages > 0 and len(self.messages) > self.max_messages:
            # Keep first message if it's system, then trim oldest
            if self.messages[0].role == "system":
                self.messages = [self.messages[0]] + self.messages[-(self.max_messages - 1) :]
            else:
                self.messages = self.messages[-self.max_messages :]

    def add_user_message(self, content: str, metadata: dict | None = None):
        """Add a user message."""
        self.add_message("user", content, metadata)

    def add_assistant_message(self, content: str, metadata: dict | None = None):
        """Add an assistant message."""
        self.add_message("assistant", content, metadata)

    def get_context(self, include_system: bool = True) -> list[Message]:
        """
        Get recent context window for LLM.

        Args:
            include_system: Include system message at the start

        Returns:
            List of messages within context window
        """
        # Get recent messages within context window
        recent = self.messages[-self.context_window :]

        # Add system message at the start if requested
        if include_system and self.system_message:
            return [self.system_message] + recent

        return recent

    def get_all_messages(self) -> list[Message]:
        """Get all messages in conversation."""
        return self.messages.copy()

    def get_last_message(self) -> Message | None:
        """Get the last message in conversation."""
        return self.messages[-1] if self.messages else None

    def clear(self):
        """Clear conversation history (keeps system message)."""
        self.messages.clear()

    def count_messages(self) -> int:
        """Get number of messages in history."""
        return len(self.messages)

    def to_dict(self) -> dict:
        """Convert memory to dictionary for serialization."""
        return {
            "max_messages": self.max_messages,
            "context_window": self.context_window,
            "system_message": self.system_message.to_dict() if self.system_message else None,
            "messages": [msg.to_dict() for msg in self.messages],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConversationMemory":
        """Create memory from dictionary."""
        memory = cls(
            max_messages=data["max_messages"], context_window=data["context_window"]
        )

        if data.get("system_message"):
            memory.system_message = Message.from_dict(data["system_message"])

        for msg_data in data.get("messages", []):
            message = Message.from_dict(msg_data)
            memory.messages.append(message)

        return memory

    def save_to_file(self, filepath: str):
        """Save conversation to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> "ConversationMemory":
        """Load conversation from JSON file."""
        with open(filepath) as f:
            data = json.load(f)
        return cls.from_dict(data)

    def get_summary(self) -> dict:
        """Get summary statistics about the conversation."""
        user_messages = sum(1 for msg in self.messages if msg.role == "user")
        assistant_messages = sum(1 for msg in self.messages if msg.role == "assistant")

        return {
            "total_messages": len(self.messages),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "context_size": min(len(self.messages), self.context_window),
            "has_system_message": self.system_message is not None,
        }

    def format_for_llm(self, include_system: bool = True) -> list[dict]:
        """
        Format messages for LLM API (OpenAI/Ollama format).

        Args:
            include_system: Include system message

        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        context = self.get_context(include_system=include_system)
        return [{"role": msg.role, "content": msg.content} for msg in context]


class MemoryManager:
    """
    Manages multiple conversation memories.

    Allows switching between different conversation contexts.
    """

    def __init__(self):
        """Initialize memory manager."""
        self.memories: dict[str, ConversationMemory] = {}
        self.current_name: str | None = None

    def create_memory(
        self, name: str, max_messages: int = 50, context_window: int = 20
    ) -> ConversationMemory:
        """
        Create a new conversation memory.

        Args:
            name: Name for this memory
            max_messages: Maximum messages to store
            context_window: Context window size

        Returns:
            Created memory instance
        """
        memory = ConversationMemory(max_messages, context_window)
        self.memories[name] = memory
        if self.current_name is None:
            self.current_name = name
        return memory

    def switch_memory(self, name: str) -> ConversationMemory | None:
        """
        Switch to a different conversation memory.

        Args:
            name: Name of memory to switch to

        Returns:
            Memory instance or None if not found
        """
        if name in self.memories:
            self.current_name = name
            return self.memories[name]
        return None

    def get_current_memory(self) -> ConversationMemory | None:
        """Get current active memory."""
        if self.current_name and self.current_name in self.memories:
            return self.memories[self.current_name]
        return None

    def delete_memory(self, name: str):
        """Delete a conversation memory."""
        if name in self.memories:
            del self.memories[name]
            if self.current_name == name:
                self.current_name = list(self.memories.keys())[0] if self.memories else None

    def list_memories(self) -> list[str]:
        """List all memory names."""
        return list(self.memories.keys())
