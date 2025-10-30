# Migration to Hugging Face Models

This document describes the changes made to migrate from paid APIs to free Hugging Face models.

## Changes Made

### 1. Dependencies (requirements.txt)
- **Removed**: `livekit-plugins-openai`, `livekit-plugins-deepgram`, `livekit-plugins-elevenlabs`
- **Added**: 
  - `transformers`, `torch`, `torchaudio` - For Hugging Face model loading
  - `TTS` (Coqui TTS) - For text-to-speech
  - `openai-whisper` - For speech-to-text (based on Hugging Face Whisper)
  - `scipy` - For audio resampling

### 2. Custom Implementations Created

#### `hf_stt.py` - Speech-to-Text
- Uses OpenAI Whisper (free, open-source model from Hugging Face)
- Models: tiny, base, small, medium, large
- Supports multiple languages

#### `hf_llm.py` - Language Model
- Uses Hugging Face transformers library
- Supports models like Mistral, Llama, Phi-3, TinyLlama, Zephyr
- Includes 4-bit quantization for GPU memory efficiency
- Auto-detects device (CPU/CUDA)

#### `hf_tts.py` - Text-to-Speech
- Uses Coqui TTS (free, open-source)
- Models: Glow-TTS, Tacotron2, Speedy-Speech, VITS
- Supports voice cloning (optional)
- Multiple voices and speaker options

### 3. Database Schema Changes

**Removed**:
- `elevenlabs_voice_id` field

**Added**:
- `stt_model` - Whisper model size (tiny/base/small/medium/large)
- `tts_model` - Coqui TTS model name

**Modified**:
- `llm_model` - Now stores Hugging Face model IDs (e.g., `mistralai/Mistral-7B-Instruct-v0.2`)

### 4. API Changes

Updated request/response models to use new field names:
- `AgentCreateRequest` / `AgentUpdateRequest`: Now includes `stt_model` and `tts_model`
- `AgentResponse`: Returns Hugging Face model names

### 5. Frontend Changes

Updated `AgentManager.js`:
- Replaced OpenAI model dropdown with Hugging Face models
- Added STT model selector (Whisper sizes)
- Added TTS model selector (Coqui TTS models)
- Removed ElevenLabs voice ID input

## Model Recommendations

### For Production (Good Balance):
- **LLM**: `mistralai/Mistral-7B-Instruct-v0.2`
- **STT**: `base` (Whisper)
- **TTS**: `tts_models/en/ljspeech/glow-tts`

### For Fast Response (Lower Quality):
- **LLM**: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- **STT**: `tiny` (Whisper)
- **TTS**: `tts_models/en/ljspeech/speedy-speech`

### For Best Quality (Slower):
- **LLM**: `mistralai/Mistral-7B-Instruct+, large` - Requires more GPU memory
- **STT**: `large` (Whisper) - Requires more GPU memory
- **TTS**: `tts_models/en/vctk/vits` - Multi-speaker support

## System Requirements

### GPU Memory:
- **Minimum**: 8GB VRAM (with quantization)
- **Recommended**: 16GB VRAM (for better models)
- **CPU-only**: Works but significantly slower

### First Run:
- Models will be downloaded from Hugging Face on first use
- This may take several minutes depending on model size
- Models are cached locally for subsequent runs

## Migration Steps

1. **Update dependencies**:
   ```bash
   cd app/agent
   pip install -r requirements.txt
   ```

2. **Run database migration** (if needed):
   - The schema changes require a migration
   - You may need to update existing agents manually or create a migration script

3. **Update environment variables**:
   - No API keys needed for Hugging Face (unless using gated models)
   - Set `HUGGING_FACE_HUB_TOKEN` if using gated models

4. **Test the system**:
   - Create a new agent with Hugging Face models
   - Test voice interactions
   - Monitor GPU/CPU usage and adjust models if needed

## Troubleshooting

### Model Loading Issues:
- Ensure you have sufficient disk space (models can be several GB)
- Check internet connection for initial download
- For gated models, set `HUGGING_FACE_HUB_TOKEN` environment variable

### Performance Issues:
- Use smaller models if GPU memory is limited
- Enable quantization (already enabled by default)
- Consider using CPU if GPU is unavailable (will be slower)

### Audio Quality Issues:
- Try larger Whisper models for better STT accuracy
- Use different TTS models for better voice quality
- Adjust sample rates if needed

## Notes

- All models are downloaded from Hugging Face Hub
- Models are cached in `~/.cache/huggingface/` by default
- First inference will be slower due to model loading
- The system uses lazy loading to minimize startup time

