"""
Hugging Face Whisper-based Speech-to-Text implementation for LiveKit
Uses openai-whisper which is based on Hugging Face's Whisper model
"""
import asyncio
import numpy as np
from typing import AsyncIterator, Optional
from livekit import rtc
from livekit.agents import stt
import whisper
import io
import torch

class WhisperSTT(stt.STT):
    """Whisper-based Speech-to-Text using Hugging Face model"""
    
    def __init__(
        self,
        *,
        model: str = "base",
        language: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize Whisper STT
        
        Args:
            model: Whisper model size (tiny, base, small, medium, large)
            language: Language code (e.g., "en", "es"). If None, auto-detect
            device: Device to run on ("cpu", "cuda", "mps"). Auto-detected if None
        """
        super().__init__(
            sample_rate=16000,
            num_channels=1,
        )
        
        self._model_name = model
        self._language = language
        self._device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load model (will be loaded on first use)
        self._model = None
        self._model_lock = asyncio.Lock()
    
    async def _load_model(self):
        """Lazy load the Whisper model"""
        if self._model is None:
            async with self._model_lock:
                if self._model is None:
                    print(f"📥 Loading Whisper model: {self._model_name} on {self._device}")
                    self._model = whisper.load_model(self._model_name, device=self._device)
                    print(f"✅ Whisper model loaded successfully")
    
    async def recognize(
        self,
        buffer: rtc.AudioFrame,
        *,
        language: Optional[str] = None,
    ) -> "stt.SpeechEvent":
        """Recognize speech from audio frame"""
        await self._load_model()
        
        # Convert LiveKit audio frame to numpy array
        # LiveKit audio frames have data as numpy array
        if hasattr(buffer, 'data'):
            if isinstance(buffer.data, np.ndarray):
                audio_data = buffer.data
            elif isinstance(buffer.data, list) and len(buffer.data) > 0:
                audio_data = np.array(buffer.data[0])
            else:
                audio_data = np.frombuffer(buffer.data, dtype=np.int16)
        else:
            # Fallback
            audio_data = np.frombuffer(buffer, dtype=np.int16)
        
        # Whisper expects float32 audio in range [-1.0, 1.0]
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32) / 32768.0
        
        # Run transcription
        try:
            # Use the specified language or auto-detect
            transcribe_lang = language or self._language
            
            result = await asyncio.to_thread(
                self._model.transcribe,
                audio_data,
                language=transcribe_lang,
                task="transcribe",
                fp16=False if self._device == "cpu" else True,
            )
            
            text = result["text"].strip()
            
            if not text:
                return stt.SpeechEvent(
                    type=stt.SpeechEventType.INTERIM_TRANSCRIPT,
                    alternatives=[stt.SpeechData(text="")],
                )
            
            return stt.SpeechEvent(
                type=stt.SpeechEventType.F.VALID,
                alternatives=[stt.SpeechData(text=text, language=result.get("language", "en"))],
            )
            
        except Exception as e:
            print(f"❌ Whisper transcription error: {e}")
            return stt.SpeechEvent(
                type=stt.SpeechEventType.INTERIM_TRANSCRIPT,
                alternatives=[stt.SpeechData(text="")],
            )
    
    async def stream(
        self,
        *,
        language: Optional[str] = None,
    ) -> AsyncIterator["stt.SpeechStream"]:
        """Create a streaming STT session"""
        await self._load_model()
        
        # Create a stream
        stream = WhisperStream(self._model, language or self._language, self._device)
        yield stream


class WhisperStream(stt.SpeechStream):
    """Streaming wrapper for Whisper STT"""
    
    def __init__(
        self,
        model: whisper.Whisper,
        language: Optional[str],
        device: str,
    ):
        super().__init__()
        self._model = model
        self._language = language
        self._device = device
        self._audio_buffer = []
    
    def push_frame(self, frame: rtc.AudioFrame) -> None:
        """Accumulate audio frames for transcription"""
        audio_data = frame.data[0] if len(frame.data) > 0 else frame.data
        self._audio_buffer.append(audio_data)
    
    async def flush(self) -> None:
        """Transcribe accumulated audio"""
        if not self._audio_buffer:
            return
        
        # Concatenate all audio chunks
        audio_data = np.concatenate(self._audio_buffer)
        self._audio_buffer = []
        
        # Convert to float32 if needed
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32) / 32768.0
        
        try:
            # Run transcription
            result = await asyncio.to_thread(
                self._model.transcribe,
                audio_data,
                language=self._language,
                task="transcribe",
                fp16=False if self._device == "cpu" else True,
            )
            
            text = result["text"].strip()
            
            if text:
                await self._event_feed.aclose(
                    stt.SpeechEvent(
                        type=stt.SpeechEventType.FINAL_TRANSCRIPT,
                        alternatives=[stt.SpeechData(text=text, language=result.get("language", "en"))],
                    )
                )
        except Exception as e:
            print(f"❌ Whisper streaming error: {e}")
    
    async def aclose(self) -> None:
        """Close the stream"""
        await self.flush()
        await super().aclose()

