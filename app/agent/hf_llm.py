"""
Hugging Face LLM implementation for LiveKit
Supports various open-source models like Llama, Mistral, Zephyr, etc.
"""
import asyncio
from typing import AsyncIterator, Optional
from livekit.agents import llm
from livekit.agents.llm import ChatContext, ChatMessage, ChatRole, ChoiceDelta
import uuid
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


class ChatContextManager:
    """Wrapper to make chat() work as async context manager and async iterator"""
    def __init__(self, iterator):
        self._iterator = iterator
        self._exhausted = False
        self._error_yielded = False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup if the iterator supports it
        if hasattr(self._iterator, 'aclose'):
            try:
                await self._iterator.aclose()
            except Exception:
                pass
        return False
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self._exhausted:
            raise StopAsyncIteration
        
        try:
            return await self._iterator.__anext__()
        except StopAsyncIteration:
            self._exhausted = True
            raise
        except Exception as e:
            # Catch any exceptions and handle gracefully
            print(f"❌ Error in ChatContextManager.__anext__: {e}")
            import traceback
            traceback.print_exc()
            
            # Yield error as a chunk instead of crashing
            if not self._error_yielded:
                self._error_yielded = True
                self._exhausted = True
                # Return error chunk - correct structure: ChatChunk(id=..., delta=ChoiceDelta(...))
                return llm.ChatChunk(
                    id=str(uuid.uuid4()),
                    delta=ChoiceDelta(content=f"[Error: {str(e)}]")
                )
            else:
                # Already yielded error, stop iteration
                raise StopAsyncIteration

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
                    # According to TinyLlama docs, tokenizer should support chat templates
                    self._tokenizer = AutoTokenizer.from_pretrained(
                        self._model_name,
                        trust_remote_code=True,
                    )
                    
                    # Add padding token if not present (required for generation)
                    if self._tokenizer.pad_token is None:
                        self._tokenizer.pad_token = self._tokenizer.eos_token
                        self._tokenizer.pad_token_id = self._tokenizer.eos_token_id
                    
                    # Verify chat template availability
                    if self._tokenizer.chat_template is None:
                        print(f"   ⚠️  Warning: Model {self._model_name} does not have a chat template")
                        print(f"   Using fallback formatting instead")
                    
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
        # Safety check: ensure tokenizer is loaded
        if self._tokenizer is None:
            raise RuntimeError("Tokenizer must be loaded before formatting messages")
        
        # Filter items to get only messages
        messages = [item for item in ctx.items if item.type == "message"]
        
        # Check if model supports chat template
        if self._tokenizer.chat_template is not None:
            # Use chat template
            formatted_messages = []
            for msg in messages:
                # Get text content from message (handles list of content items)
                if hasattr(msg, 'text_content') and msg.text_content:
                    content = msg.text_content
                elif hasattr(msg, 'content'):
                    # Handle content as list
                    if isinstance(msg.content, list):
                        content = " ".join([str(c) for c in msg.content if isinstance(c, str)])
                    else:
                        content = str(msg.content)
                else:
                    content = ""
                
                role_map = {
                    "user": "user",
                    "assistant": "assistant",
                    "system": "system",
                    "developer": "system",
                }
                formatted_messages.append({
                    "role": role_map.get(msg.role, "user"),
                    "content": content,
                })
            
            formatted = self._tokenizer.apply_chat_template(
                formatted_messages,
                tokenize=False,
                add_generation_prompt=True,
            )
            return formatted
        else:
            # Fallback formatting
            text = ""
            for msg in messages:
                # Get text content from message
                if hasattr(msg, 'text_content') and msg.text_content:
                    content = msg.text_content
                elif hasattr(msg, 'content'):
                    if isinstance(msg.content, list):
                        content = " ".join([str(c) for c in msg.content if isinstance(c, str)])
                    else:
                        content = str(msg.content)
                else:
                    content = ""
                
                if msg.role == "system" or msg.role == "developer":
                    text += f"System: {content}\n\n"
                elif msg.role == "user":
                    text += f"User: {content}\n\n"
                elif msg.role == "assistant":
                    text += f"Assistant: {content}\n\n"
            
            text += "Assistant: "
            return text
    
    async def _chat_impl(
        self,
        *,
        chat_ctx: ChatContext,
        conn_options: Optional[object] = None,
        fnc_ctx: Optional[object] = None,
        tools: Optional[list] = None,
        tool_choice: Optional[str] = None,
        **kwargs,
    ) -> AsyncIterator[llm.ChatChunk]:
        """Internal chat implementation that yields chunks"""
        try:
            await self._load_model()
            
            # Ensure tokenizer is loaded before formatting
            if self._tokenizer is None:
                raise RuntimeError("Tokenizer not loaded after _load_model()")
            
            # Format messages
            prompt = self._format_messages(chat_ctx)
            
            # Tokenize with proper truncation for context window
            # TinyLlama has 2048 token context window
            max_input_length = 2048 - self._max_tokens - 50  # Reserve space for generation
            inputs = self._tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=max_input_length
            )
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            # Stop tokens - according to TinyLlama docs, uses EOS token
            stop_token_ids = []
            if self._tokenizer.eos_token_id:
                stop_token_ids.append(self._tokenizer.eos_token_id)
            if self._tokenizer.pad_token_id and self._tokenizer.pad_token_id != self._tokenizer.eos_token_id:
                stop_token_ids.append(self._tokenizer.pad_token_id)
            
            # Additional stop sequences for TinyLlama (common chat patterns)
            # These help prevent model from generating unwanted tokens
            if hasattr(self._tokenizer, 'encode'):
                # Add user/system message markers as stop tokens if they exist
                try:
                    # TinyLlama uses specific tokens for chat formatting
                    user_token = self._tokenizer.encode("<|user|>", add_special_tokens=False)
                    assistant_token = self._tokenizer.encode("<|assistant|>", add_special_tokens=False)
                    stop_token_ids.extend(user_token)
                    stop_token_ids.extend(assistant_token)
                except:
                    pass  # Skip if tokens don't exist
            
            stopping_criteria = StoppingCriteriaList([StopOnTokens(stop_token_ids)])
            
            # MAXIMUM SPEED settings - target 5 second total response
            # Sacrifice quality for speed
            with torch.no_grad():
                output_ids = self._model.generate(
                    **inputs,
                    max_new_tokens=self._max_tokens,
                    temperature=0.5,  # Lower = faster, more deterministic
                    do_sample=True,
                    top_p=0.85,  # Lower for faster convergence
                    top_k=10,  # Very low for MAXIMUM speed (only top 10 tokens)
                    repetition_penalty=1.2,  # Higher to end quickly
                    num_beams=1,  # Greedy = fastest
                    early_stopping=True,
                    stopping_criteria=stopping_criteria,
                    pad_token_id=self._tokenizer.pad_token_id,
                    eos_token_id=self._tokenizer.eos_token_id,
                    use_cache=True,  # Enable KV cache for faster generation
                )
            
            # Decode response
            input_length = inputs["input_ids"].shape[1]
            generated_ids = output_ids[0][input_length:]
            
            # Decode with skip_special_tokens to remove special tokens
            # According to docs, this is important for chat models
            response_text = self._tokenizer.decode(
                generated_ids, 
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True  # Clean up spacing
            )
            
            # Clean up the response (remove any artifacts)
            response_text = response_text.strip()
            
            # Yield chunks FASTER for quicker response
            # Stream in larger chunks to reduce overhead
            words = response_text.split()
            
            # Stream in larger batches for MAXIMUM speed
            if words:
                batch_size = 5  # Send 5 words at a time for fastest delivery
                for i in range(0, len(words), batch_size):
                    batch = words[i:i + batch_size]
                    chunk_text = " ".join(batch) + " "
                    
                    # NO delay for maximum speed
                    # (removed asyncio.sleep for instant streaming)
                    
                    yield llm.ChatChunk(
                        id=str(uuid.uuid4()),
                        delta=ChoiceDelta(content=chunk_text)
                    )
            else:
                # Fallback: yield entire response if no words
                if response_text.strip():
                    yield llm.ChatChunk(
                        id=str(uuid.uuid4()),
                        delta=ChoiceDelta(content=response_text)
                    )
        except Exception as e:
            print(f"❌ Hugging Face LLM error: {e}")
            import traceback
            traceback.print_exc()
            # Yield error message as final chunk
            try:
                yield llm.ChatChunk(
                    id=str(uuid.uuid4()),
                    delta=ChoiceDelta(content=f"I apologize, but I encountered an error: {str(e)}")
                )
            except Exception as yield_error:
                # If even yielding fails, log and stop
                print(f"❌ Failed to yield error chunk: {yield_error}")
                # Don't re-raise - let it stop gracefully
                return
    
    def chat(
        self,
        *,
        chat_ctx: ChatContext,
        conn_options: Optional[object] = None,
        fnc_ctx: Optional[object] = None,
        tools: Optional[list] = None,
        tool_choice: Optional[str] = None,
        **kwargs,  # Catch any other parameters LiveKit might pass
    ):
        """Generate chat response - returns async context manager that is also an async iterator"""
        # Return wrapped async iterator that supports both protocols
        iterator = self._chat_impl(
            chat_ctx=chat_ctx,
            conn_options=conn_options,
            fnc_ctx=fnc_ctx,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs
        )
        return ChatContextManager(iterator)
