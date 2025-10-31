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
import torch
import io

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
            capabilities=stt.STTCapabilities(streaming=False, interim_results=False)
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
    
    async def _recognize_impl(
        self,
        buffer: rtc.AudioFrame,
        *,
        language: Optional[str] = None,
        conn_options: Optional[object] = None,
    ) -> "stt.SpeechEvent":
        """Recognize speech from audio frame (required by LiveKit STT abstract class)"""
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
                type=stt.SpeechEventType.FINAL_TRANSCRIPT,
                alternatives=[stt.SpeechData(text=text, language=result.get("language", "en"))],
            )
            
        except Exception as e:
            print(f"❌ Whisper transcription error: {e}")
            return stt.SpeechEvent(
                type=stt.SpeechEventType.INTERIM_TRANSCRIPT,
                alternatives=[stt.SpeechData(text="")],
            )
    
    def stream(
        self,
        *,
        language: Optional[str] = None,
        conn_options: Optional[object] = None,
    ) -> "stt.RecognizeStream":
        """Create a streaming STT session - non-async method that returns a stream"""
        # Return a RecognizeStream that will handle the transcription
        from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS
        conn_options = conn_options or DEFAULT_API_CONNECT_OPTIONS
        
        return WhisperStream(
            stt=self,
            language=language or self._language,
            conn_options=conn_options,
        )


class WhisperStream(stt.RecognizeStream):
    """Streaming wrapper for Whisper STT - implements RecognizeStream interface"""
    
    def __init__(
        self,
        *,
        stt: "WhisperSTT",
        language: Optional[str],
        conn_options: object,
    ):
        super().__init__(stt=stt, conn_options=conn_options)
        self._stt_plugin = stt
        self._language = language
        self._audio_buffer = []
        self._model_loaded = False
    
    async def _run(self) -> None:
        """
        Main processing loop - reads audio from _input_ch and sends events to _event_ch
        This is called by the RecognizeStream base class
        """
        # Load model if not already loaded
        print("🎤 Whisper STT stream started - waiting for audio...")
        
        if not self._model_loaded:
            await self._stt_plugin._load_model()
            self._model_loaded = True
        
        # Process audio frames from the input channel
        async for data in self._input_ch:
            if isinstance(data, self._FlushSentinel):
                # Flush signal received - transcribe accumulated audio
                print(f"🔄 Flush signal received - transcribing {len(self._audio_buffer)} audio chunks...")
                
                if not self._audio_buffer:
                    continue
                
                # Concatenate all audio chunks
                audio_data = np.concatenate(self._audio_buffer)
                self._audio_buffer = []
                
                # Convert to float32 if needed
                if audio_data.dtype != np.float32:
                    audio_data = audio_data.astype(np.float32) / 32768.0
                
                print(f"🎧 Audio data shape: {audio_data.shape}, dtype: {audio_data.dtype}")
                
                try:
                    # Send START_OF_SPEECH event
                    self._event_ch.send_nowait(
                        stt.SpeechEvent(type=stt.SpeechEventType.START_OF_SPEECH)
                    )
                    print("📢 START_OF_SPEECH event sent")
                    
                    # Run transcription
                    print("🔄 Running Whisper transcription...")
                    result = await asyncio.to_thread(
                        self._stt_plugin._model.transcribe,
                        audio_data,
                        language=self._language,
                        task="transcribe",
                        fp16=False if self._stt_plugin._device == "cpu" else True,
                    )
                    
                    text = result["text"].strip()
                    print(f"✅ Transcription result: '{text}'")
                    
                    if text:
                        # Send END_OF_SPEECH event
                        self._event_ch.send_nowait(
                            stt.SpeechEvent(type=stt.SpeechEventType.END_OF_SPEECH)
                        )
                        
                        # Send FINAL_TRANSCRIPT event
                        self._event_ch.send_nowait(
                            stt.SpeechEvent(
                                type=stt.SpeechEventType.FINAL_TRANSCRIPT,
                                alternatives=[
                                    stt.SpeechData(
                                        text=text,
                                        language=result.get("language", self._language or "en")
                                    )
                                ],
                            )
                        )
                        print(f"📝 FINAL_TRANSCRIPT event sent: '{text}'")
                    else:
                        print("⚠️  No text transcribed (silence or unclear audio)")
                        
                except Exception as e:
                    print(f"❌ Whisper transcription error: {e}")
                    import traceback
                    traceback.print_exc()
                    
            elif isinstance(data, rtc.AudioFrame):
                # Accumulate audio frame
                audio_data = data.data[0] if len(data.data) > 0 else data.data
                self._audio_buffer.append(audio_data)
                print(f"🎤 Audio frame received (buffer size: {len(self._audio_buffer)})")
        
        print("🛑 Input channel closed - stream ending")

