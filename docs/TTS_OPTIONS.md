# Text-to-Speech (TTS) Options

This document explains the TTS options available for Liquid ASCII.

## Current Implementation: edge-tts (Online)

**Default TTS engine** - Already integrated and working.

### Pros
- ✓ Highest quality (neural voices)
- ✓ 322+ voices in 100+ languages
- ✓ Natural-sounding speech
- ✓ Provides word timestamps for perfect lip sync
- ✓ Free to use
- ✓ No setup required

### Cons
- ✗ Requires internet connection
- ✗ Depends on Microsoft's service availability

### Usage
```bash
# Already works out of the box
./dev.sh run --speak "Hello world"

# List all voices
./dev.sh run --list-voices

# Use specific voice
./dev.sh run --speak "Bonjour" --voice fr-FR-DeniseNeural
```

---

## Offline Option 1: pyttsx3 (System TTS)

**Lightweight offline TTS** - Uses your system's built-in voices.

### Pros
- ✓ Very small (~50KB)
- ✓ Works completely offline
- ✓ Fast synthesis
- ✓ No model downloads needed
- ✓ Uses system voices (SAPI5/Windows, NSSpeech/macOS, espeak/Linux)

### Cons
- ✗ Lower quality (robotic sound)
- ✗ Limited voices (depends on OS)
- ✗ No word timing data (basic lip sync estimation only)

### Installation
```bash
uv pip install pyttsx3

# Linux also needs espeak
sudo apt install espeak
```

### Usage
```python
from src.audio.tts_offline import OfflineTTSEngine

engine = OfflineTTSEngine()

# List available voices
voices = engine.list_voices()
for voice in voices:
    print(voice['name'])

# Synthesize
result = await engine.synthesize("Hello, offline world!")
print(result['audio_path'])
```

---

## Offline Option 2: Piper TTS (Neural Quality)

**High-quality offline neural TTS** - Best offline option.

### Pros
- ✓ High quality neural voices
- ✓ Works completely offline
- ✓ Fast inference (~100ms/second of audio)
- ✓ Multiple voices and languages
- ✓ Open source

### Cons
- ✗ Larger downloads (~50-100MB per voice)
- ✗ Requires piper binary installation
- ✗ Limited word timing data

### Installation

**Linux:**
```bash
# Download piper binary
wget https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz
tar -xzf piper_linux_x86_64.tar.gz
sudo mv piper/piper /usr/local/bin/

# Download a voice model
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

**Usage:**
```bash
# Synthesize with piper
echo "Hello world" | piper --model en_US-lessac-medium.onnx --output_file output.wav
```

---

## Offline Option 3: Coqui TTS (Best Quality, Largest)

**State-of-the-art neural TTS** - Research-grade quality.

### Pros
- ✓ Highest quality offline TTS
- ✓ Voice cloning capabilities
- ✓ Multiple languages
- ✓ Active development

### Cons
- ✗ Large models (~500MB-1GB)
- ✗ Slower inference
- ✗ Higher memory usage
- ✗ Complex setup

### Installation
```bash
uv pip install TTS

# Download models on first use (automatic)
```

### Usage
```python
from TTS.api import TTS

# Initialize (downloads model on first run)
tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")

# Synthesize
tts.tts_to_file(text="Hello world", file_path="output.wav")
```

---

## Comparison Table

| Feature | edge-tts | pyttsx3 | Piper | Coqui TTS |
|---------|----------|---------|-------|-----------|
| **Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Offline** | ✗ | ✓ | ✓ | ✓ |
| **Size** | 0 MB | <1 MB | 50-100 MB | 500MB-1GB |
| **Speed** | Fast | Very Fast | Fast | Slow |
| **Setup** | None | Minimal | Medium | Complex |
| **Word Timing** | ✓ Perfect | ✗ None | ~ Basic | ~ Basic |
| **Voices** | 322+ | 3-10 | 50+ | 100+ |
| **Lip Sync Quality** | Perfect | Basic | Good | Good |
| **Recommended For** | Default | Quick/Simple | Offline Quality | Research/Custom |

---

## Recommendations

### For Most Users: **edge-tts** (current default)
- Best quality-to-convenience ratio
- Works out of the box
- Perfect lip sync
- Just needs internet

### For Offline Use: **Piper**
- Best offline quality
- Reasonable size
- Good performance
- Install instructions above

### For Quick/Simple: **pyttsx3**
- Already created: `src/audio/tts_offline.py`
- Instant setup
- Good for testing/development
- Lower quality but works everywhere

### For Research/Custom: **Coqui TTS**
- Best quality possible
- Voice cloning
- Custom models
- Requires more resources

---

## Integration Example

To add pyttsx3 to the main app:

1. **Install**: `uv pip install pyttsx3`

2. **Add to requirements.txt**:
   ```
   pyttsx3>=2.90  # Optional: offline TTS
   ```

3. **Modify src/main.py** to add `--offline` flag:
   ```python
   parser.add_argument('--offline', action='store_true',
                      help='Use offline TTS (pyttsx3)')
   ```

4. **Use in code**:
   ```python
   if args.offline:
       from src.audio.tts_offline import OfflineTTSEngine
       tts_engine = OfflineTTSEngine()
   else:
       from src.audio.tts import EdgeTTSEngine
       tts_engine = EdgeTTSEngine()
   ```

---

## Testing TTS Engines

### Test edge-tts (current)
```bash
./dev.sh run --speak "Testing Edge TTS"
```

### Test pyttsx3 (after installation)
```bash
python src/audio/tts_offline.py
```

### Test piper (after installation)
```bash
echo "Testing Piper TTS" | piper --model <model-path> --output_file test.wav
```

---

## Notes

- **No LLM needed**: TTS converts text to audio, not text generation
- **Current system works great**: edge-tts is already integrated and excellent
- **Offline is optional**: Only needed if you must work without internet
- **Quality tradeoff**: Online (edge-tts) > Offline Neural (Piper/Coqui) > System (pyttsx3)

Choose based on your needs:
- **Have internet?** → Use edge-tts (current default)
- **Need offline?** → Use Piper (best quality) or pyttsx3 (smallest)
- **Development/testing?** → Use pyttsx3 (instant setup)
