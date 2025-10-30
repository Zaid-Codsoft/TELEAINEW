"""
Google Gemini LLM implementation for LiveKit
Uses Google's Gemini API for language model
"""
import asyncio
from typing import AsyncIterator, Optional
from livekit.agents import llm
from livekit.agents.llm import ChatContext, ChatMessage, ChatRole
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
import os

class GeminiLLM(llm.LLM):
    """Google Gemini LLM for LiveKit agents"""
    
    def __init__(
        self,
        *,
        model: str = "gemini-1.5-flash",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ):
        """
        Initialize Gemini LLM
        
        Args:
            model: Gemini model name (e.g., "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro")
            api_key: Google API key (or set GEMINI_API_KEY env var)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
        """
        super().__init__()
        
        self._model_name = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        
        # Get API key
        self._api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self._api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Set it as environment variable or pass api_key parameter."
            )
        
        # Configure Gemini
        genai.configure(api_key=self._api_key)
        
        # Lazy loading
        self._model = None
        self._model_lock = asyncio.Lock()
    
    async def _load_model(self):
        """Lazy load the Gemini model"""
        if self._model is None:
            async with self._model_lock:
                if self._model is None:
                    print(f"📥 Loading Gemini model: {self._model_name}")
                    try:
                        self._model = genai.GenerativeModel(self._model_name)
                        # Configure generation settings
                        generation_config = {
                            "temperature": self._temperature,
                            "max_output_tokens": self._max_tokens,
                        }
                        self._generation_config = generation_config
                        print(f"✅ Gemini model loaded successfully")
                    except Exception as e:
                        print(f"❌ Failed to load Gemini model: {e}")
                        raise
    
    def _format_messages(self, ctx: ChatContext) -> list:
        """Format chat messages for Gemini"""
        messages = []
        
        # Add system instruction if present
        system_content = None
        for msg in ctx.messages:
            if msg.role == ChatRole.SYSTEM:
                system_content = msg.content
                break
        
        # Format messages for Gemini (alternating user/assistant)
        for msg in ctx.messages:
            if msg.role == ChatRole.SYSTEM:
                # System messages are handled separately
                continue
            elif msg.role == ChatRole.USER:
                messages.append({"role": "user", "parts": [msg.content]})
            elif msg.role == ChatRole.ASSISTANT:
                messages.append({"role": "model", "parts": [msg.content]})
        
        return messages, system_content
    
    async def chat(
        self,
        ctx: ChatContext,
        fnc_ctx: Optional[object] = None,  # FunctionContext not needed for Gemini
    ) -> AsyncIterator[llm.ChatChunk]:
        """Generate chat response using Gemini"""
        await self._load_model()
        
        # Format messages
        messages, system_content = self._format_messages(ctx)
        
        try:
            # Start chat if there's history
            if len(messages) > 1:
                # Use chat context
                chat = self._model.start_chat(history=messages[:-1])
                user_message = messages[-1]["parts"][0]
                
                # Configure with system instruction if present
                config = {
                    **self._generation_config,
                }
                if system_content:
                    config["system_instruction"] = system_content
                
                # Generate response
                response = await asyncio.to_thread(
                    chat.send_message,
                    user_message,
                    generation_config=genai.types.GenerationConfig(**config),
                )
            else:
                # Single message
                user_message = messages[0]["parts"][0] if messages else ""
                
                # Configure with system instruction if present
                config = {
                    **self._generation_config,
                }
                if system_content:
                    config["system_instruction"] = system_content
                
                # Generate response
                response = await asyncio.to_thread(
                    self._model.generate_content,
                    user_message,
                    generation_config=genai.types.GenerationConfig(**config),
                )
            
            # Stream the response text in chunks
            response_text = response.text if hasattr(response, 'text') else ""
            
            if not response_text:
                # Try to get text from parts
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        parts = candidate.content.parts
                        response_text = "".join(part.text for part in parts if hasattr(part, 'text'))
            
            # Yield chunks for streaming-like behavior
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
            print(f"❌ Gemini LLM error: {e}")
            import traceback
            traceback.print_exc()
            yield llm.ChatChunk(
                choices=[
                    llm.Choice(
                        delta=llm.ChatDelta(content=f"Error: {str(e)}"),
                        index=0,
                    )
                ]
            )

