# BrainCX Voice Agent - Hugging Face Free Models Implementation

This implementation replaces all paid APIs (OpenAI, Deepgram, ElevenLabs) with free, open-source models from Hugging Face.

## Overview

The agent now uses:
- **STT (Speech-to-Text)**: OpenAI Whisper (open-source, hosted on Hugging Face)
- **LLM (Language Model)**: Mistral, Llama, Phi-3, or other Hugging Face models
- **TTS (Text-to-Speech)**: Coqui TTS (free, open-source)

## Quick Start

### 1. Install Dependencies

```bash
cd app/agent
pip install -r requirements.txt
```

**Note**: This will install PyTorch, transformers, and other ML libraries. For GPU support, ensure CUDA is installed.

### 2. Environment Setup

No API keys are required! However, if you want to use gated models on Hugging Face, set:

```bash
export HUGGING_FACE_HUB_TOKEN="your_token_here"
```

### 3. Run the Agent

```bash
python simple_agent.py dev  # Development mode
# or
python simple_agent.py start  # Production mode
```

## Model Selection

### ⚡ **Default (Smallest & Fastest)** - Recommended for Quick Setup:
- **LLM**: `TinyLlama/TinyLlama-1.1B-Chat-v1.0` (~600MB)
- **STT**: `tiny` (Whisper) (~150MB)
- **TTS**: `tts_models/en/ljspeech/speedy-speech` (~50MB)
- **Total**: ~800MB download

### **Balanced**:
- **LLM**: `mistralai/Mistral-7B-Instruct-v0.2` (~14GB)
- **STT**: `base` (Whisper) (~150MB)
- **TTS**: `tts_models/en/ljspeech/glow-tts` (~50MB)

### **Best Quality** (Requires more GPU memory):
- **LLM**: `mistralai/Mistral-7B-Instruct-v0.2` or larger
- **STT**: `large` (Whisper) (~3GB)
- **TTS**: `tts_models/en/vctk/vits` (~200MB)

**Note**: The simple agent uses the smallest models by default. See `SIMPLE_SETUP.md` for details.

## Available Models

### LLM Models (Language Models)

| Model | Size | Speed | Quality | Memory Required |
|-------|------|-------|---------|----------------|
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | 1.1B | Very Fast | Good | ~2GB |
| `microsoft/Phi-3-mini-4k-instruct` | 3.8B | Fast | Very Good | ~4GB |
| `mistralai/Mistral-7B-Instruct-v0.2` | 7B | Medium | Excellent | ~8GB |
| `HuggingFaceH4/zephyr-7b-beta` | 7B | Medium | Excellent | ~8GB |

**Note**: Models with quantization enabled use ~50% less memory.

### STT Models (Whisper)

| Model | Parameters | Speed | Accuracy | Memory |
|-------|-----------|-------|----------|--------|
| `tiny` | 39M | Fastest | Good | ~1GB |
| `base` | 74M | Fast | Very Good | ~1GB |
| `small` | 244M | Medium | Excellent | ~2GB |
| `medium` | 769M | Slow | Excellent | ~5GB |
| `large` | 1550M | Slowest | Best | ~10GB |

### TTS Models (Coqui TTS)

| Sex Model | Speed | Quality | Notes |
|-----------|-------|---------|-------|
| `tts_models/en/ljspeech/speedy-speech` | Fastest | Good | Real-time capable |
| `tts_models/en/ljspeech/glow-tts` | Fast | Very Good | **Recommended** |
| `tts_models/en/ljspeech/tacotron2-DDC` | Medium | Very Good | Classic model |
| `tts_models/en/vctk/vits` | Medium | Excellent | Multi-speaker support |

## System Requirements

### Minimum Requirements (CPU-only):
- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 8GB (16GB recommended)
- **Disk**: 20GB free space (for model downloads)
- **Speed**: Slower but functional

### Recommended Requirements (GPU):
- **GPU**: NVIDIA GPU with 8GB+ VRAM (16GB recommended)
- **CUDA**: Version 11.8 or 12.1+
- **RAM**: 16GB迅
- **Disk**: 50GB free space
- **Speed**: Real-time or near real-time

### For Best Quality (High-End):
- **GPU**: NVIDIA GPU with 24GB+ VRAM
- **RAM**: 32GB+
- **Disk**: 100GB+ free space

## First Run

On the first run, models will be automatically downloaded from Hugging Face Hub:

1. **LLM Model**: ~4-14GB (depending on model)
2. **Whisper Model**: ~150MB - 3GB (depending on size)
3. **TTS Model**: ~50-200MB

**Total Download**: ~5-20GB depending on models selected.

Models are cached in:
- Linux/Mac: `~/.cache/huggingface/`
- Windows: `C:\Users\<username>\.cache\huggingface\`

## Configuration

### Via API/Frontend

When creating an agent through the web interface, you can select:
- LLM model from dropdown
- STT model (Whisper size)
- TTS model (Coqui TTS)
- Temperature for LLM
- Locale/language

### Via Code

In `simple_agent.py`, the default configuration is set in `get_agent_config()`:

```python
{
    "llm_model": "mistralai/Mistral-7B-Instruct-v0.2",
    "stt_model": "base",
    "tts_model": "tts_models/en/ljspeech/glow-tts",
    "temperature": 0.7,
    "locale": "en-US",
}
```

## Troubleshooting

### Model Download Issues

**Problem**: Models fail to download
**Solutions**:
- Check internet connection
- Verify disk space is sufficient
- For gated models, set `HUGGING_FACE_HUB_TOKEN`
- Try downloading models manually: `huggingface-cli download <model_name>`

### Out of Memory Errors

**Problem**: GPU runs out of memory
**Solutions**:
- Use smaller models (tiny Whisper, TinyLlama)
- Enable quantization (already enabled by default)
- Reduce batch size
- Use CPU instead (slower but works)

### Slow Performance

**Problem**: Agent responds slowly
**Solutions**:
- Use smaller/faster models
- Enable GPU acceleration
- Use quantization
- Reduce model complexity

### Audio Quality Issues

**Problem**: Poor speech recognition or synthesis
**Solutions**:
- Use larger Whisper model (small/medium/large)
- Try different TTS models
- Ensure good audio input quality
- Check microphone settings

## Performance Benchmarks

### Typical Response Times (GPU):

| Configuration | First Response | Subsequent |
|--------------|---------------|------------|
| TinyLlama + tiny Whisper + speedy-speech | ~2-3s | ~1s |
| Mistral-7B + base Whisper + glow-tts | ~3-5s | ~1.5s |
| Mistral-7B + large Whisper + vits | ~5-8s | ~2-3s |

### CPU-only Performance:

| Configuration | First Response | Subsequent |
|--------------|---------------|------------|
| TinyLlama + tiny Whisper + speedy-speech | ~5-8s | ~3-5s |
| Mistral-7B + base Whisper + glow-tts | ~10-15s | ~5-8s |

**Note**: First response includes model loading time.

## Advanced Configuration

### Custom Model Paths

You can download models locally and reference them:

```python
# In hf_llm.py or simple_agent.py
llm=HuggingFaceLLM(
    model="/path/to/local/model",
    ...
)
```

### Language Support

Whisper supports 100+ languages. Set the language in agent config:

```python
locale="es-ES"  # Spanish
locale="fr-FR"  # French
locale="de-DE"  # German
# etc.
```

The language code is automatically extracted (e.g., "en-US" -> "en").

### Voice Cloning (Advanced)

Coqui TTS supports voice cloning with a reference audio file:

```python
tts=CoquiTTSPlugin(
    model="tts_models/en/ljspeech/glow-tts",
    voice_cloning=True,
    speaker_wav="/path/to/reference.wav",
)
```

## Migration from Paid APIs

If migrating from the old paid API version:

1. **Database Migration**: Update existing agents to use new model names
2. **No API Keys Needed**: Remove OpenAI, Deepgram, ElevenLabs API keys
3. **Model Download**: First run will download models (one-time)
4. **Performance**: May be slower than paid APIs but completely free

See `MIGRATION_NOTES.md` for detailed migration steps.

## Support & Resources

### Documentation:
- Hugging Face: https://huggingface.co/docs
- Whisper: https://github.com/openai/whisper
- Coqui TTS: https://github.com/coqui-ai/TTS
- LiveKit Agents: https://docs.livekit.io/agents/

### Model Hub:
- Browse models: https://huggingface.co/models
- Search for: "text-generation", "automatic-speech-recognition", "text-to-speech"

## License

All models used are open-source and free for commercial use:
- Whisper: MIT License (OpenAI)
- Mistral: Apache 2.0
- Coqui TTS: MPL 2.0

## Notes

- Models are cached after first download
- GPU acceleration significantly improves performance
- Quantization reduces memory usage by ~50%
- All processing happens locally (no data sent to external APIs)
- Completely free and open-source

