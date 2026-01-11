"""
Chat bot controller for interactive conversations.

Integrates personality, memory, and LLM backend for character-based chat.
"""

from collections.abc import AsyncIterator

from .llm import LLMBackend, create_llm_backend
from .memory import ConversationMemory
from .personality import get_personality, get_system_prompt


class ChatBot:
    """
    Main chat bot controller.

    Manages conversation flow, integrating character personality,
    memory, and LLM backend.
    """

    def __init__(
        self,
        character_name: str = "default",
        llm_backend: LLMBackend | None = None,
        memory: ConversationMemory | None = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ):
        """
        Initialize chat bot.

        Args:
            character_name: Name of character personality to use
            llm_backend: LLM backend (auto-created if None)
            memory: Conversation memory (auto-created if None)
            temperature: LLM temperature setting
            max_tokens: Maximum tokens per response
        """
        self.character_name = character_name
        self.personality = get_personality(character_name)

        # Create LLM backend if not provided
        if llm_backend is None:
            # Try to auto-detect available backend
            try:
                llm_backend = create_llm_backend("ollama")
                if not llm_backend.is_available():
                    raise Exception("Ollama not available")
            except Exception:
                try:
                    llm_backend = create_llm_backend("openai")
                except Exception as e:
                    raise Exception(
                        "No LLM backend available. "
                        "Install Ollama or set OPENAI_API_KEY environment variable."
                    ) from e

        self.llm_backend = llm_backend

        # Create memory if not provided
        if memory is None:
            memory = ConversationMemory(max_messages=50, context_window=20)

        self.memory = memory
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Set system prompt based on personality
        system_prompt = get_system_prompt(character_name)
        self.memory.set_system_message(system_prompt)

    async def chat(self, user_message: str, stream: bool = False) -> str:
        """
        Send a message and get response.

        Args:
            user_message: User's message
            stream: Whether to stream response

        Returns:
            Bot's response
        """
        # Add user message to memory
        self.memory.add_user_message(user_message)

        # Get conversation context
        messages = self.memory.format_for_llm(include_system=True)

        # Generate response
        if stream:
            # For streaming, collect full response
            response_parts = []
            async for token in self.llm_backend.stream_generate(
                messages, temperature=self.temperature, max_tokens=self.max_tokens
            ):
                response_parts.append(token)
            response = "".join(response_parts)
        else:
            response = await self.llm_backend.generate(
                messages, temperature=self.temperature, max_tokens=self.max_tokens
            )

        # Add assistant response to memory
        self.memory.add_assistant_message(response)

        return response

    async def chat_stream(self, user_message: str) -> AsyncIterator[str]:
        """
        Send message and stream response tokens.

        Args:
            user_message: User's message

        Yields:
            Response tokens as they're generated
        """
        # Add user message to memory
        self.memory.add_user_message(user_message)

        # Get conversation context
        messages = self.memory.format_for_llm(include_system=True)

        # Stream response
        response_parts = []
        async for token in self.llm_backend.stream_generate(
            messages, temperature=self.temperature, max_tokens=self.max_tokens
        ):
            response_parts.append(token)
            yield token

        # Add complete response to memory
        full_response = "".join(response_parts)
        self.memory.add_assistant_message(full_response)

    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of text to suggest expression.

        Args:
            text: Text to analyze

        Returns:
            Suggested expression name
        """
        text_lower = text.lower()

        # Positive expressions
        if any(
            word in text_lower
            for word in ["happy", "joy", "excited", "great", "wonderful", "love", "amazing"]
        ):
            return "happy"

        # Sad expressions
        if any(word in text_lower for word in ["sad", "sorry", "unfortunately", "regret"]):
            return "sad"

        # Angry expressions
        if any(word in text_lower for word in ["angry", "frustrated", "annoyed", "upset", "wrong"]):
            return "angry"

        # Surprised expressions
        if any(
            word in text_lower
            for word in ["wow", "surprising", "unexpected", "amazing", "!!", "incredible"]
        ):
            return "surprised"

        # Thinking expressions
        if any(
            word in text_lower
            for word in ["think", "consider", "perhaps", "maybe", "hmm", "let me"]
        ):
            return "thinking"

        # Default neutral
        return "neutral"

    def suggest_expression_from_response(self, response: str) -> str:
        """
        Suggest expression based on bot's response.

        Args:
            response: Bot's response text

        Returns:
            Suggested expression name
        """
        return self.analyze_sentiment(response)

    def get_conversation_summary(self) -> dict:
        """Get summary of current conversation."""
        return {
            "character": self.character_name,
            "personality": self.personality.description,
            "memory_stats": self.memory.get_summary(),
            "llm_backend": type(self.llm_backend).__name__,
        }

    def clear_conversation(self):
        """Clear conversation history while keeping system prompt."""
        self.memory.clear()

    def set_temperature(self, temperature: float):
        """
        Set LLM temperature.

        Args:
            temperature: Temperature value (0-1)
        """
        self.temperature = max(0.0, min(1.0, temperature))

    def set_max_tokens(self, max_tokens: int):
        """
        Set maximum tokens per response.

        Args:
            max_tokens: Maximum token count
        """
        self.max_tokens = max(50, min(2000, max_tokens))


class ChatSession:
    """
    High-level chat session manager.

    Handles multi-turn conversations with automatic expression updates.
    """

    def __init__(
        self,
        character_name: str = "default",
        backend_type: str = "ollama",
        backend_kwargs: dict | None = None,
    ):
        """
        Initialize chat session.

        Args:
            character_name: Character to chat with
            backend_type: LLM backend type ("ollama" or "openai")
            backend_kwargs: Additional backend arguments
        """
        backend_kwargs = backend_kwargs or {}

        try:
            llm_backend = create_llm_backend(backend_type, **backend_kwargs)
        except Exception as e:
            raise Exception(f"Failed to create LLM backend: {e}") from e

        self.bot = ChatBot(character_name=character_name, llm_backend=llm_backend)
        self.current_expression = "neutral"

    async def send_message(self, message: str, stream: bool = False) -> tuple[str, str]:
        """
        Send message and get response with suggested expression.

        Args:
            message: User's message
            stream: Whether to stream response

        Returns:
            Tuple of (response, suggested_expression)
        """
        response = await self.bot.chat(message, stream=stream)
        expression = self.bot.suggest_expression_from_response(response)
        self.current_expression = expression
        return response, expression

    async def send_message_stream(self, message: str) -> AsyncIterator[tuple[str, str]]:
        """
        Send message and stream response with expression updates.

        Args:
            message: User's message

        Yields:
            Tuples of (token, current_expression)
        """
        accumulated = []
        async for token in self.bot.chat_stream(message):
            accumulated.append(token)
            # Update expression based on accumulated text periodically
            if len(accumulated) % 10 == 0:
                partial_text = "".join(accumulated)
                expression = self.bot.analyze_sentiment(partial_text)
                self.current_expression = expression
            yield token, self.current_expression

        # Final expression based on complete response
        full_response = "".join(accumulated)
        self.current_expression = self.bot.analyze_sentiment(full_response)

    def get_current_expression(self) -> str:
        """Get current suggested expression."""
        return self.current_expression

    def clear(self):
        """Clear conversation history."""
        self.bot.clear_conversation()
        self.current_expression = "neutral"
