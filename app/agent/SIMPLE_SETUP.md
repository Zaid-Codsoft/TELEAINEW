# Simple Agent Setup - Small Models

This is a simplified version using the **smallest, fastest-downloading models** available.

## Model Sizes & Download Times

### Total Download: ~800MB (instead of 5-20GB)

1. **LLM (Language Model)**: TinyLlama-1.1B
   - Size: ~600MB
   - Download: ~2-5 minutes
   - Quality: Good for basic conversations
   
2. **STT (Speech-to-Text)**: Whisper Tiny
   - Size: ~150MB  
   - Download: ~30-60 seconds
   - Quality: Good accuracy for clear speech
   
3. **TTS (Text-to-Speech)**: Speedy Speech
   - Size: ~50MB
   - Download: ~10-30 seconds
   - Quality: Good, real-time capable

## Quick Start

### 1. Create Virtual Environment (Recommended)

**Windows:**
```powershell
cd app\agent
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
cd app/agent
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run the Agent

```bash
python simple_agent.py dev
```

That's it! The agent will:
- Download models automatically on first run (~800MB total)
- Work completely offline after download
- No API keys or external services needed

## What Changed from Full Version

✅ **Simplified**: No API calls, no database configuration  
✅ **Small Models**: Uses smallest available models  
✅ **Fast Setup**: ~800MB download vs 5-20GB  
✅ **Single Agent**: One hardcoded agent configuration  
✅ **No Agent Manager**: Removed frontend complexity  

## Configuration

The agent configuration is hardcoded in `simple_agent.py`:

```python
{
    "name": "Simple Voice Assistant",
    "llm_model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # ~600MB
    "stt_model": "tiny",                                 # ~150MB
    "tts_model": "tts_models/en/ljspeech/speedy-speech", # ~50MB
    "temperature": 0.7,
    "locale": "en-US",
}
```

To change the configuration, edit `get_agent_config()` in `simple_agent.py`.

## Performance

### Response Times (GPU):
- First response: ~2-3 seconds (includes model loading)
- Subsequent responses: ~1 second

### Response Times (CPU):
- First response: ~5-8 seconds
- Subsequent responses: ~3-5 seconds

## System Requirements

### Minimum:
- **RAM**: 4GB (8GB recommended)
- **Disk**: 2GB free space
- **CPU**: Any modern CPU works
- **GPU**: Optional (much faster with GPU)

### GPU Benefits:
- 3-5x faster inference
- Better for real-time conversations
- Not required - works fine on CPU

## Features

✅ Basic conversational AI  
✅ Weather lookup (if API key provided)  
✅ Math calculations  
✅ Voice input/output  
✅ No external API dependencies  

## Notes

- Models download to `~/.cache/huggingface/` (Linux/Mac) or `C:\Users\<username>\.cache\huggingface\` (Windows)
- First run will take longer due to model downloads
- After first run, everything is cached and fast
- All processing is local - completely private
- No data sent to external services (except weather API if used)

## Troubleshooting

**Slow downloads?**  
- Check internet connection
- Models download from Hugging Face Hub (may be slower in some regions)

**Out of memory?**  
- Use CPU instead of GPU
- Models are already smallest available

**Want better quality?**  
- Edit `simple_agent.py` to use larger models (see `README_HF.md` for options)
- Note: Larger models = larger downloads (5-20GB)

## Next Steps

The agent is ready to use! Just:
1. Create virtual environment and install dependencies (see above)
2. Run `python simple_agent.py dev`
3. Start a voice call through your LiveKit client

