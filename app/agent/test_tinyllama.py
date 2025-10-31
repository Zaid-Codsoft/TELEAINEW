#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script to verify actual TinyLlama LLM functionality"""
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("Testing TinyLlama LLM - Actual Working Code")
print("=" * 60)

# Test 1: Load tokenizer
print("\n1. Loading tokenizer...")
try:
    tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    print("✅ Tokenizer loaded")
    
    # Check chat template
    if tokenizer.chat_template is None:
        print("⚠️  No chat template found")
    else:
        print("✅ Chat template available")
    
    # Check padding token
    if tokenizer.pad_token is None:
        print("⚠️  No pad token, setting to EOS token")
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
    
    print(f"   EOS token: {tokenizer.eos_token_id}")
    print(f"   PAD token: {tokenizer.pad_token_id}")
except Exception as e:
    print(f"❌ Error loading tokenizer: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 2: Format messages
print("\n2. Formatting messages...")
try:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
    
    if tokenizer.chat_template:
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        print("✅ Chat template applied")
        print(f"   Prompt preview: {prompt[:150]}...")
    else:
        # Fallback formatting
        prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                prompt += f"System: {msg['content']}\n\n"
            elif msg["role"] == "user":
                prompt += f"User: {msg['content']}\n\n"
        prompt += "Assistant: "
        print("⚠️  Using fallback formatting")
        print(f"   Prompt preview: {prompt[:150]}...")
except Exception as e:
    print(f"❌ Error formatting messages: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 3: Tokenize
print("\n3. Tokenizing...")
try:
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    print(f"✅ Tokenized: input_ids shape {inputs['input_ids'].shape}")
    print(f"   Input length: {inputs['input_ids'].shape[1]} tokens")
except Exception as e:
    print(f"❌ Error tokenizing: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 4: Load model (CPU only for testing)
print("\n4. Loading model (CPU, this may take a moment)...")
try:
    device = "cpu"  # Use CPU for testing
    model = AutoModelForCausalLM.from_pretrained(
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
        trust_remote_code=True,
    )
    model = model.to(device)
    model.eval()
    print("✅ Model loaded")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 5: Generate
print("\n5. Generating response (this may take a moment on CPU)...")
try:
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=50,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    
    # Decode
    input_length = inputs["input_ids"].shape[1]
    generated_ids = outputs[0][input_length:]
    response = tokenizer.decode(generated_ids, skip_special_tokens=True)
    
    print("✅ Generation successful")
    print(f"   Response: {response[:200]}...")
except Exception as e:
    print(f"❌ Error generating: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("✅ All TinyLlama tests passed!")
print("=" * 60)

