"""
Hugging Face LLM implementation for LiveKit
Supports various open-source models like Llama, Mistral, Zephyr, etc.
"""
import asyncio
from typing import AsyncIterator, Optional
from livekit.agents import llm
from livekit.agents.llm import ChatContext, ChatMessage, ChatRole
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TextStreamer,
    StoppingCriteria,
    StoppingCriteriaList,
)
import threading
from queue import Queue

class StopOnTokens(StoppingCriteria):
    """Stop generation when certain tokens are encountered"""
    def __init__(self, stop_token_ids: list):
        self.stop_token_ids = stop_token_ids
    
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        for stop_id in self.stop_token_ids:
            if input_ids[0][-1] == stop_id:
                return True
        return False


class HuggingFaceLLM(llm.LLM):
    """Hugging Face LLM for LiveKit agents"""
    
    def __init__(
        self,
        *,
        model: str = "mistralai/Mistral-7B-Instruct-v0.2",
        temperature: float = 0.7,
        device: Optional[str] = None,
        use_quantization: bool = True,
        max_tokens: int = 512,
    ):
        """
        Initialize Hugging Face LLM
        
        Args:
            model: Hugging Face model ID (e.g., "mistralai/Mistral-7B-Instruct-v0.2")
            temperature: Sampling temperature
            device: Device to run on ("cpu", "cuda", "mps"). Auto-detected if None
            use_quantization: Use 4-bit quantization to reduce memory usage
            max_tokens: Maximum tokens to generate
        """
        super().__init__()
        
        self._model_name = model
        self._temperature = temperature
        self._device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._use_quantization = use_quantization and self._device == "cuda"
        self._max_tokens = max_tokens
        
        # Lazy loading
        self._tokenizer = None
        self._model = None
        self._model_lock = asyncio.Lock()
        
        # Common chat template models
        self._chat_template_models = [
            "mistralai",
            "meta-llama",
            "HuggingFaceH4",
            "microsoft",
        ]
    
    async def _load_model(self):
        """Lazy load the Hugging Face model"""
        if self._model is None:
            async with self._model_lock:
                if self._model is None:
                    print(f"📥 Loading Hugging Face model: {self._model_name}")
                    print(f"   Device: {self._device}, Quantization: {self._use_quantization}")
                    
                    # Load tokenizer
                    self._tokenizer = AutoTokenizer.from_pretrained(
                        self._model_name,
                        trust_remote_code=True,
                    )
                    
                    # Add padding token if not present
                    if self._tokenizer.pad_token is None:
                        self._tokenizer.pad_token = self._tokenizer.eos_token
                    
                    # Configure quantization for GPU
                    quantization_config = None
                    if self._use_quantization:
                        quantization_config = BitsAndBytesConfig(
                            load_in_4bit=True,
                            bnb_4bit_compute_dtype=torch.float16,
                            bnb_4bit_use_double_quant=True,
                            bnb_4bit_quant_type="nf4",
                        )
                    
                    # Load model
                    self._model = AutoModelForCausalLM.from_pretrained(
                        self._model_name,
                        quantization_config=quantization_config,
                        device_map="auto" if self._device == "cuda" else None,
                        torch_dtype=torch.float16 if self._device == "cuda" else torch.float32,
                        trust_remote_code=True,
                        low_cpu_mem_usage=True,
                    )
                    
                    if self._device == "cpu":
                        self._model = self._model.to(self._device)
                    
                    print(f"✅ Model loaded successfully")
    
    def _format_messages(self, ctx: ChatContext) -> str:
        """Format chat messages for the model"""
        # Check if model supports chat template
        if self._tokenizer.chat_template is not None:
            # Use chat template
            messages = []
            for msg in ctx.messages:
                role_map = {
                    ChatRole.USER: "user",
                    ChatRole.ASSISTANT: "assistant",
                    ChatRole.SYSTEM: "system",
                }
                messages.append({
                    "role": role_map.get(msg.role, "user"),
                    "content": msg.content,
                })
            
            formatted = self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
            return formatted
        else:
            # Fallback formatting
            text = ""
            for msg in ctx.messages:
                if msg.role == ChatRole.SYSTEM:
                    text += f"System: {msg.content}\n\n"
                elif msg.role == ChatRole.USER:
                    text += f"User: {msg.content}\n\n"
                elif msg.role == ChatRole.ASSISTANT:
                    text += f"Assistant: {msg.content}\n\n"
            
            text += "Assistant: "
            return text
    
    async def chat(
        self,
        ctx: ChatContext,
        fnc_ctx: Optional[llm.FunctionContext] = None,
    ) -> AsyncIterator[llm.ChatChunk]:
        """Generate chat response"""
        await self._load_model()
        
        # Format messages
        prompt = self._format_messages(ctx)
        
        # Tokenize
        inputs = self._tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
        inputs = {k: v.to(self._device) for k, v in inputs.items()}
        
        # Stop tokens
        stop_token_ids = []
        if self._tokenizer.eos_token_id:
            stop_token_ids.append(self._tokenizer.eos_token_id)
        if self._tokenizer.pad_token_id and self._tokenizer.pad_token_id != self._tokenizer.eos_token_id:
            stop_token_ids.append(self._tokenizer.pad_token_id)
        
        stopping_criteria = StoppingCriteriaList([StopOnTokens(stop_token_ids)])
        
        # Generate
        try:
            with torch.no_grad():
                output_ids = self._model.generate(
                    **inputs,
                    max_new_tokens=self._max_tokens,
                    temperature=self._temperature,
                    do_sample=True if self._temperature > 0 else False,
                    top_p=0.9,
                    stopping_criteria=stopping_criteria,
                    pad_token_id=self._tokenizer.pad_token_id,
                )
            
            # Decode response
            input_length = inputs["input_ids"].shape[1]
            generated_ids = output_ids[0][input_length:]
            response_text = self._tokenizer.decode(generated_ids, skip_special_tokens=True)
            
            # Yield chunks
            # For streaming-like behavior, yield in chunks
            chunk_size = 10
            for i in range(0, len(response_text), chunk_size):
                chunk_text = response_text[i:i + chunk_size]
                if chunk_text.strip():
                    await asyncio.sleep(0)  # Yield control
                    yield llm.ChatChunk(
                        choices=[
                            llm.Choice(
                                delta=llm.ChatDelta(content=chunk_text),
                                index=0,
                            )
                        ]
                    )
            
        except Exception as e:
            print(f"❌ Hugging Face LLM error: {e}")
            yield llm.ChatChunk(
                choices=[
                    llm.Choice(
                        delta=llm.ChatDelta(content=f"Error: {str(e)}"),
                        index=0,
                    )
                ]
            )
