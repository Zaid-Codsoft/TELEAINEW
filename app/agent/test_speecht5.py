#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script to verify actual SpeechT5 TTS functionality"""
import sys
import torch
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("Testing SpeechT5 TTS - Actual Working Code")
print("=" * 60)

# Test 1: Load models
print("\n1. Loading models...")
try:
    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    print("✅ Processor loaded")
    
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
    print("✅ Model loaded")
    
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
    print("✅ Vocoder loaded")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    exit(1)

# Test 2: Load speaker embeddings
print("\n2. Loading speaker embeddings...")
try:
    embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
    speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)
    print(f"✅ Speaker embeddings loaded: shape {speaker_embeddings.shape}")
except Exception as e:
    print(f"⚠️  Warning: Could not load speaker embeddings: {e}")
    print("   Creating zero embedding as fallback...")
    speaker_embeddings = torch.zeros(1, 512)

# Test 3: Process text
print("\n3. Processing text...")
try:
    text = "Hello, this is a test."
    inputs = processor(text=text, return_tensors="pt")
    print(f"✅ Text processed: input_ids shape {inputs['input_ids'].shape}")
    print(f"   Input keys: {list(inputs.keys())}")
except Exception as e:
    print(f"❌ Error processing text: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 4: Generate speech
print("\n4. Generating speech...")
try:
    model.eval()
    with torch.no_grad():
        speech = model.generate_speech(
            inputs["input_ids"],
            speaker_embeddings,
            vocoder=vocoder
        )
    print(f"✅ Speech generated: shape {speech.shape}, dtype {speech.dtype}")
    print(f"   Min: {speech.min().item():.4f}, Max: {speech.max().item():.4f}")
    print(f"   Mean: {speech.mean().item():.4f}")
except Exception as e:
    print(f"❌ Error generating speech: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("✅ All SpeechT5 tests passed!")
print("=" * 60)

