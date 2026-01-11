"""Chat package - LLM-powered conversation system"""

from .bot import ChatBot, ChatSession
from .llm import (
    LLMBackend,
    OllamaBackend,
    OpenAIBackend,
    create_llm_backend,
    list_available_backends,
)
from .memory import (
    Message,
    ConversationMemory,
    MemoryManager,
)
from .personality import (
    CharacterPersonality,
    get_personality,
    get_system_prompt,
    get_all_personalities,
    PERSONALITIES,
)
from .voice_chat import (
    VoiceChatController,
    SentenceChunker,
    SpeechChunk,
    stream_with_voice,
    chunk_text_for_tts,
)

__all__ = [
    # Bot
    "ChatBot",
    "ChatSession",
    # LLM backends
    "LLMBackend",
    "OllamaBackend",
    "OpenAIBackend",
    "create_llm_backend",
    "list_available_backends",
    # Memory
    "Message",
    "ConversationMemory",
    "MemoryManager",
    # Personality
    "CharacterPersonality",
    "get_personality",
    "get_system_prompt",
    "get_all_personalities",
    "PERSONALITIES",
    # Voice Chat
    "VoiceChatController",
    "SentenceChunker",
    "SpeechChunk",
    "stream_with_voice",
    "chunk_text_for_tts",
]
