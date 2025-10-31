#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pre-download all models locally before running the agent
This ensures models are ready and avoids waiting during first run
"""
import os
import sys
import torch

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    SpeechT5Processor,
    SpeechT5ForTextToSpeech,
    SpeechT5HifiGan,
)
from datasets import load_dataset
import whisper

def download_whisper_model(model_size: str = "tiny"):
    """Download Whisper STT model"""
    print(f"\n{'='*60}")
    print(f"📥 Downloading Whisper STT model: {model_size}")
    print(f"{'='*60}")
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   Device: {device}")
        print(f"   This may take 1-3 minutes...")
        
        model = whisper.load_model(model_size, device=device)
        print(f"✅ Whisper model '{model_size}' downloaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Error downloading Whisper model: {e}")
        return False

def download_tts_models():
    """Download SpeechT5 TTS models"""
    print(f"\n{'='*60}")
    print(f"📥 Downloading SpeechT5 TTS models")
    print(f"{'='*60}")
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   Device: {device}")
        
        print(f"   Downloading processor and model...")
        processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
        print(f"   ✅ Processor and model downloaded")
        
        print(f"   Downloading vocoder...")
        vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
        print(f"   ✅ Vocoder downloaded")
        
        print(f"   Note: Speaker embeddings will be downloaded on first use")
        print(f"   (They're small and can be cached during runtime)")
        
        print(f"✅ All TTS models downloaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Error downloading TTS models: {e}")
        import traceback
        traceback.print_exc()
        return False

def download_llm_model(model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
    """Download Hugging Face LLM model"""
    print(f"\n{'='*60}")
    print(f"📥 Downloading LLM model: {model_name}")
    print(f"{'='*60}")
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   Device: {device}")
        print(f"   This may take 2-10 minutes depending on model size...")
        
        print(f"   Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
        )
        print(f"   ✅ Tokenizer downloaded")
        
        print(f"   Downloading model (this is the largest download)...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
        )
        print(f"   ✅ Model downloaded")
        
        print(f"✅ LLM model '{model_name}' downloaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Error downloading LLM model: {e}")
        import traceback
        traceback.print_exc()
        return False

def download_vad_model():
    """Download Silero VAD model (used by LiveKit)"""
    print(f"\n{'='*60}")
    print(f"📥 Downloading Silero VAD model")
    print(f"{'='*60}")
    try:
        from livekit.plugins import silero
        print(f"   Downloading VAD model...")
        vad = silero.VAD.load()
        print(f"✅ VAD model downloaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Error downloading VAD model: {e}")
        return False

def main():
    """Main function to download all models"""
    print("="*60)
    print("🚀 Tele-AI Model Downloader")
    print("="*60)
    print("\nThis script will download all required models locally.")
    print("Models will be cached in your Hugging Face cache directory.")
    print("\nModels to download:")
    print("  - Whisper STT (tiny): ~150MB")
    print("  - SpeechT5 TTS: ~100MB")
    print("  - TinyLlama LLM: ~600MB (optional)")
    print("  - Silero VAD: ~10MB")
    print("  - Total: ~860MB")
    print("\n" + "="*60)
    
    # Check if user wants to download LLM
    download_llm = False
    if len(sys.argv) > 1 and sys.argv[1] == "--with-llm":
        download_llm = True
        print("\n⚠️  LLM download enabled (large download ~600MB)")
    else:
        print("\n💡 Tip: Add --with-llm flag to also download LLM model")
        print("   Example: python download_models.py --with-llm")
    
    print("\nStarting downloads...\n")
    
    success_count = 0
    total_count = 3 + (1 if download_llm else 0)
    
    # Download Whisper STT
    if download_whisper_model("tiny"):
        success_count += 1
    
    # Download TTS models
    if download_tts_models():
        success_count += 1
    
    # Download VAD
    if download_vad_model():
        success_count += 1
    
    # Download LLM (optional)
    if download_llm:
        if download_llm_model("TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
            success_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Download Summary")
    print(f"{'='*60}")
    print(f"✅ Successfully downloaded: {success_count}/{total_count}")
    
    if success_count == total_count:
        print(f"\n🎉 All models downloaded successfully!")
        print(f"💾 Models are cached and ready to use.")
        print(f"\nYou can now run the agent:")
        print(f"   python simple_agent.py dev")
    else:
        print(f"\n⚠️  Some models failed to download.")
        print(f"   The agent will download them automatically on first use.")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    main()

