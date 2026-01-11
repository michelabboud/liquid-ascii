# New Features: Stages 9-11

This document describes features implemented in Stages 9-11 of development.

## Table of Contents

- [Stage 9: Voice Personality Matching](#stage-9-voice-personality-matching)
- [Stage 10: Package Distribution](#stage-10-package-distribution)
- [Stage 11: Chat Mode](#stage-11-chat-mode)

---

## Stage 9: Voice Personality Matching

Automatically select appropriate TTS voices based on character appearance and personality.

### Features

- **Character-Specific Voice Selection**: Each of the 12 characters has a carefully selected default voice that matches their personality
- **Automatic Voice Assignment**: When using `--speak` or `--tutor`, the voice is auto-selected based on character unless explicitly overridden
- **Voice Discovery**: List all character-to-voice mappings with `--list-character-voices`

### Usage

```bash
# Auto-select voice based on character (alien gets alien-appropriate voice)
./dev.sh run --speak "Greetings, Earthling" --character alien

# Override with specific voice if desired
./dev.sh run --speak "Hello!" --character cat --voice en-US-GuyNeural

# View all character→voice mappings
./dev.sh run --list-character-voices
```

### Character Voice Mappings

| Character | Voice                 | Personality                    |
|-----------|-----------------------|--------------------------------|
| default   | en-US-AriaNeural      | Balanced, friendly, neutral    |
| round     | en-AU-NatashaNeural   | Cheerful, bubbly, warm         |
| tall      | en-GB-RyanNeural      | Dignified, formal, British     |
| wide      | en-US-DavisNeural     | Laid-back, deep, relaxed       |
| robot     | en-US-GuyNeural       | Technical, precise, masculine  |
| cute      | en-US-JennyNeural     | Young, energetic, playful      |
| alien     | en-US-TonyNeural      | Analytical, otherworldly       |
| cat       | en-US-SaraNeural      | Independent, clever, feminine  |
| dog       | en-US-ChristopherNeural | Enthusiastic, loyal          |
| baby      | en-US-AnaNeural       | Young, innocent, soft          |
| elder     | en-GB-LibbyNeural     | Wise, mature, patient          |
| skull     | en-US-EricNeural      | Deep, mysterious, dark         |

### Implementation Details

The voice selection system is implemented in `src/model/head.py`:

- **`default_voice` property**: Returns character-specific voice
- **`_get_character_voice()` static method**: Maps character names to voices
- **`get_all_character_voices()` static method**: Returns complete mapping for display

The CLI integration in `src/main.py` automatically uses `head.default_voice` when `--voice` is not specified.

---

## Stage 10: Package Distribution

Production-ready packaging, containerization, and automated release system.

### Features

1. **PyPI Package** - Installable via `pip install liquid-ascii`
2. **Docker Images** - Multi-platform container distribution
3. **Docker Compose** - Pre-configured service definitions
4. **GitHub Actions** - Automated testing, building, and releasing
5. **Build Documentation** - Comprehensive distribution guide

### PyPI Package

**Published Package Configuration:**
- Package name: `liquid-ascii`
- Version: 0.2.0
- Development status: Beta
- Python requirement: >=3.11

**Installation:**
```bash
pip install liquid-ascii
liquid-ascii --help
liquid-ascii --speak "Hello from PyPI!"
```

**Optional Dependencies:**
```bash
# Development tools
pip install liquid-ascii[dev]

# Testing only
pip install liquid-ascii[test]

# Linting only
pip install liquid-ascii[lint]
```

### Docker Distribution

**Dockerfile Features:**
- Multi-stage build for size optimization
- Python 3.11 slim base
- PortAudio for audio support
- Non-root user for security
- Optimized layer caching

**Building:**
```bash
docker build -t liquid-ascii:latest .
```

**Running:**
```bash
# Demo mode
docker run -it --rm liquid-ascii:latest

# With audio (Linux)
docker run -it --rm --device /dev/snd liquid-ascii:latest --speak "Hello!"

# Custom character
docker run -it --rm liquid-ascii:latest --character alien
```

### Docker Compose

Pre-configured profiles for common use cases:

```bash
# Demo mode
docker-compose --profile demo up

# Speak mode
docker-compose --profile speak up

# Interactive mode
docker-compose --profile interactive up

# Different characters
docker-compose --profile alien up
docker-compose --profile robot up
docker-compose --profile cute up

# Development shell
docker-compose --profile dev up
```

**docker-compose.yml** includes configurations for:
- Demo, speak, interactive, tutor modes
- Character showcases (alien, cute, robot)
- Benchmark testing
- Development environment

### GitHub Actions Workflows

**Automated Release Process (.github/workflows/release.yml):**

Triggered on version tags (e.g., `v0.2.0`):

1. **Build and Test**
   - Runs full test suite
   - Executes linters (ruff, mypy)
   - Builds Python package

2. **Publish to PyPI**
   - Uploads to PyPI automatically
   - Uses `PYPI_API_TOKEN` secret

3. **Create GitHub Release**
   - Generates release notes
   - Attaches distribution artifacts
   - Publishes release

4. **Build Docker Images**
   - Multi-platform build (amd64, arm64)
   - Pushes to GitHub Container Registry
   - Tags: `latest` and version-specific

**Creating a Release:**
```bash
# 1. Update version in pyproject.toml
vim pyproject.toml  # Set version to 0.2.0

# 2. Commit changes
git add pyproject.toml
git commit -m "Bump version to 0.2.0"

# 3. Create and push tag
git tag v0.2.0
git push origin v0.2.0

# 4. GitHub Actions automatically handles the rest
```

### Build Scripts Documentation

Complete distribution guide in `BUILD.md`:
- Local package building
- Docker image creation
- PyPI publication (manual and automated)
- GitHub release process
- Troubleshooting common issues

---

## Stage 11: Chat Mode

Interactive conversation system with LLM integration and personality-driven responses.

### Features

- **LLM Integration**: Support for Ollama (local) and OpenAI APIs
- **Character Personalities**: 12 unique personalities with distinct speaking styles
- **Conversation Memory**: Context-aware multi-turn conversations
- **Dynamic Expressions**: Character expressions change based on sentiment
- **Streaming Responses**: Real-time token streaming for responsive UX

### Quick Start

**Prerequisites:**

Option 1 - Ollama (Local):
```bash
# Install Ollama (https://ollama.ai)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Download a model
ollama pull llama3.2
```

Option 2 - OpenAI:
```bash
# Set API key
export OPENAI_API_KEY='your-api-key-here'
```

**Usage:**

```bash
# Basic chat (uses Ollama by default)
./dev.sh run --chat

# Chat with specific character
./dev.sh run --chat --character robot

# Use OpenAI backend
./dev.sh run --chat --llm-backend openai

# Specify model
./dev.sh run --chat --llm-backend ollama --llm-model mistral

# Check available backends
./dev.sh run --list-llm-backends
```

### Character Personalities

Each character has a unique personality that influences their conversation style:

#### Default
- **Traits**: Friendly, helpful, clear, professional
- **Style**: Clear and articulate with warm tone
- **Example**: "Hello! How can I help you today?"

#### Round
- **Traits**: Jolly, optimistic, enthusiastic, warm
- **Style**: Bubbly and enthusiastic with positivity
- **Example**: "Oh, how wonderful! That's fantastic!"

#### Tall
- **Traits**: Dignified, wise, thoughtful, measured
- **Style**: Formal with philosophical undertones
- **Example**: "Allow me to consider that carefully."

#### Wide
- **Traits**: Relaxed, casual, friendly, easygoing
- **Style**: Casual and informal language
- **Example**: "Hey there! Sure thing, I got you."

#### Robot
- **Traits**: Logical, precise, technical, analytical
- **Style**: Technical and precise structure
- **Example**: "Processing your inquiry... Analysis indicates..."

#### Cute
- **Traits**: Playful, energetic, adorable, enthusiastic
- **Style**: Cute and playful with expressions
- **Example**: "Ooh, this is so exciting! Yay!"

#### Alien
- **Traits**: Curious, analytical, otherworldly, fascinated
- **Style**: Scientific curiosity, external perspective
- **Example**: "Fascinating! On my planet... Your species is most intriguing."

#### Cat
- **Traits**: Independent, clever, playful, selective
- **Style**: Clever and independent with feline charm
- **Example**: "Hmm, I suppose I could help you. Very well, if you insist."

#### Dog
- **Traits**: Loyal, enthusiastic, friendly, eager
- **Style**: Enthusiastic and loyal with boundless energy
- **Example**: "Oh boy! I can help with that! Yes! Let's do this together!"

#### Baby
- **Traits**: Innocent, curious, simple, wonder
- **Style**: Simple and innocent with childlike wonder
- **Example**: "Ooh, what's that? Wow, that's amazing!"

#### Elder
- **Traits**: Wise, patient, experienced, thoughtful
- **Style**: Wise and patient with life experience
- **Example**: "Ah, in my many years... Let me share some wisdom."

#### Skull
- **Traits**: Mysterious, philosophical, dark, profound
- **Style**: Dark and philosophical, existential themes
- **Example**: "In the grand scheme of existence... From beyond the veil..."

### Chat Commands

During a conversation:
- **Type normally**: Send messages to the character
- **`quit` or `exit`**: End the conversation
- **`clear`**: Clear conversation history

### Dynamic Expression System

The character's facial expression automatically changes based on conversation sentiment:

- **Happy**: Positive words (happy, joy, excited, wonderful)
- **Sad**: Negative emotions (sad, sorry, unfortunately)
- **Angry**: Frustration (angry, frustrated, wrong)
- **Surprised**: Excitement (wow, surprising, incredible)
- **Thinking**: Contemplation (think, consider, maybe, hmm)
- **Neutral**: Default state

Expressions update in real-time as the LLM streams responses.

### Architecture

**Chat Module Structure (`src/chat/`):**

1. **personality.py**: Character personality definitions
   - `CharacterPersonality` dataclass
   - System prompts for each character
   - Personality trait definitions

2. **memory.py**: Conversation memory management
   - `Message` dataclass for conversation history
   - `ConversationMemory` with sliding window
   - Save/load conversations to JSON

3. **llm.py**: LLM backend interface
   - `LLMBackend` abstract class
   - `OllamaBackend` for local inference
   - `OpenAIBackend` for cloud API
   - Streaming and batch generation

4. **bot.py**: Chat bot controller
   - `ChatBot` integrates personality + memory + LLM
   - `ChatSession` manages multi-turn conversations
   - Sentiment analysis for expression suggestions

### API Usage

**Python API Example:**

```python
from src.chat import ChatSession
import asyncio

async def chat_example():
    # Create chat session
    session = ChatSession(
        character_name="alien",
        backend_type="ollama",
        backend_kwargs={"model": "llama3.2:latest"}
    )

    # Send message
    response, expression = await session.send_message("Hello, alien friend!")
    print(f"Response: {response}")
    print(f"Expression: {expression}")

    # Streaming response
    print("Streaming:", end=" ")
    async for token, expr in session.send_message_stream("Tell me about your planet"):
        print(token, end="", flush=True)
    print()

    # Clear conversation
    session.clear()

asyncio.run(chat_example())
```

**Direct Bot Usage:**

```python
from src.chat import ChatBot, OllamaBackend, ConversationMemory

# Create components
backend = OllamaBackend(model="llama3.2:latest")
memory = ConversationMemory(max_messages=50, context_window=20)
bot = ChatBot(
    character_name="robot",
    llm_backend=backend,
    memory=memory,
    temperature=0.7
)

# Chat
response = await bot.chat("What is your purpose?")
print(response)

# Analyze sentiment
expression = bot.analyze_sentiment(response)
print(f"Suggested expression: {expression}")
```

### Configuration

**LLM Backend Selection:**
- Ollama: Local, private, free (requires installation)
- OpenAI: Cloud-based, fast, requires API key

**Memory Configuration:**
- `max_messages`: Total messages to store (default: 50)
- `context_window`: Messages sent to LLM (default: 20)

**Generation Parameters:**
- `temperature`: Randomness 0-1 (default: 0.7)
- `max_tokens`: Response length limit (default: 500)

### Performance Notes

- **Ollama**:
  - First response slower (~2-5s)
  - Subsequent responses faster
  - Depends on local hardware
  - Recommended models: llama3.2, mistral, phi

- **OpenAI**:
  - Faster responses (~1-2s)
  - Consistent latency
  - Requires internet connection
  - Recommended models: gpt-4o-mini, gpt-4o

### Troubleshooting

**Ollama not connecting:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Download model if needed
ollama pull llama3.2
```

**OpenAI authentication error:**
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Set if missing
export OPENAI_API_KEY='your-key'
```

**Character not responding:**
- Check LLM backend is available
- Verify model is downloaded (for Ollama)
- Check internet connection (for OpenAI)
- Review error messages in terminal

---

## Combined Usage Examples

### Voice Personality + Chat

```bash
# Chat with alien character using its default voice
./dev.sh run --chat --character alien

# The alien personality will:
# - Use analytical, curious speaking style
# - Have alien-appropriate TTS voice (en-US-TonyNeural)
# - Show appropriate expressions based on conversation
```

### Distribution + Chat

```bash
# Run chat mode from Docker
docker-compose run --rm liquid-ascii-base --chat --character robot

# Install from PyPI and chat
pip install liquid-ascii
liquid-ascii --chat --character elder --llm-backend openai
```

### Full Feature Showcase

```bash
# Elder character with chat, custom quality, and color scheme
./dev.sh run --chat \
  --character elder \
  --quality high \
  --scheme warm \
  --llm-backend ollama \
  --llm-model llama3.2
```

---

## Future Enhancements

Potential improvements for future releases:

### Chat Mode
- **Voice + Chat Integration**: Speak LLM responses aloud with lip sync
- **Multi-modal Chat**: Include images, files in conversation
- **Conversation Persistence**: Save/load chat history across sessions
- **Custom Personalities**: User-defined character personalities
- **Multi-Character Chat**: Characters talking to each other

### Distribution
- **Homebrew Formula**: macOS package manager distribution
- **Windows Installer**: Standalone executable with installer
- **Snap/Flatpak**: Linux universal packages
- **Web Version**: Browser-based demo (WebAssembly)

### Voice & Personality
- **Voice Cloning**: Custom voice generation per character
- **Emotion Detection**: Advanced sentiment analysis
- **Voice Modulation**: Real-time pitch/tone adjustments
- **Multi-language Support**: Personalities in different languages

---

## Version History

- **0.1.0**: Initial release (Stages 1-8)
- **0.2.0**: Voice personality, distribution, chat mode (Stages 9-11)

---

## API Documentation

### Chat Module

Full API documentation for the chat system:

**src.chat.ChatSession**
```python
class ChatSession(character_name, backend_type, backend_kwargs)
    """High-level chat session manager."""

    async send_message(message: str, stream: bool) -> tuple[str, str]
    async send_message_stream(message: str) -> AsyncIterator[tuple[str, str]]
    get_current_expression() -> str
    clear() -> None
```

**src.chat.ChatBot**
```python
class ChatBot(character_name, llm_backend, memory, temperature, max_tokens)
    """Main chat bot controller."""

    async chat(user_message: str, stream: bool) -> str
    async chat_stream(user_message: str) -> AsyncIterator[str]
    analyze_sentiment(text: str) -> str
    suggest_expression_from_response(response: str) -> str
    get_conversation_summary() -> dict
    clear_conversation() -> None
```

**src.chat.OllamaBackend**
```python
class OllamaBackend(model, base_url)
    """Ollama backend for local LLM."""

    async generate(messages, temperature, max_tokens) -> str
    async stream_generate(messages, temperature, max_tokens) -> AsyncIterator[str]
    is_available() -> bool
```

**src.chat.OpenAIBackend**
```python
class OpenAIBackend(model, api_key)
    """OpenAI API backend."""

    async generate(messages, temperature, max_tokens) -> str
    async stream_generate(messages, temperature, max_tokens) -> AsyncIterator[str]
    is_available() -> bool
```

**src.chat.ConversationMemory**
```python
class ConversationMemory(max_messages, context_window)
    """Manages conversation history."""

    set_system_message(content: str) -> None
    add_user_message(content: str, metadata: dict) -> None
    add_assistant_message(content: str, metadata: dict) -> None
    get_context(include_system: bool) -> List[Message]
    format_for_llm(include_system: bool) -> List[dict]
    save_to_file(filepath: str) -> None
    load_from_file(filepath: str) -> ConversationMemory
```

---

## Credits

Stages 9-11 implementation includes:
- Character personality system design
- Voice-to-character matching
- Docker containerization
- GitHub Actions CI/CD
- Ollama and OpenAI integrations
- Sentiment-based expression system
- Streaming chat interface

---

For more information:
- [Main README](../README.md)
- [Features Documentation](FEATURES.md) (Stages 5-8)
- [Build Guide](../BUILD.md)
- [Installation Guide](../INSTALL.md)
