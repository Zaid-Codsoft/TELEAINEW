"""
Hugging Face Text-to-Speech implementation for LiveKit
Uses transformers with SpeechT5 models (Python 3.13 compatible)
"""
import asyncio
import numpy as np
from typing import AsyncIterator, Optional
from livekit import rtc
from livekit.agents import tts
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torch
from datasets import load_dataset
import soundfile as sf

class SpeechT5TTSPlugin(tts.TTS):
    """SpeechT5 TTS implementation for LiveKit using transformers"""
    
    def __init__(
        self,
        *,
        model: str = "microsoft/speecht5_tts",
        vocoder: str = "microsoft/speecht5_hifigan",
        speaker_embedding: Optional[str] = None,
        device: Optional[str] = None,
        speed: float = 1.0,  # Speech speed: 1.0 = normal, <1.0 = slower, >1.0 = faster
    ):
        """
        Initialize SpeechT5 TTS
        
        Args:
            model: TTS model name from Hugging Face
            vocoder: Vocoder model name (converts features to audio)
            speaker_embedding: Pre-computed speaker embedding or dataset name
            device: Device to run on ("cpu", "cuda"). Auto-detected if None
            speed: Speech speed multiplier (1.0 = normal, 0.8 = 20% slower, 1.2 = 20% faster)
        """
        self._sample_rate = 16000  # SpeechT5 default sample rate
        self._num_channels = 1
        self._speed = max(0.5, min(2.0, speed))  # Clamp speed between 0.5x and 2.0x
        
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=False),  # Non-streaming for simplicity
            sample_rate=self._sample_rate,
            num_channels=self._num_channels,
        )
        self._model_name = model
        self._vocoder_name = vocoder
        self._speaker_embedding = speaker_embedding
        self._device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Lazy loading
        self._processor = None
        self._model = None
        self._vocoder = None
        self._speaker_emb = None
        self._model_lock = asyncio.Lock()
    
    async def _load_model(self):
        """Lazy load the TTS models"""
        if self._model is None:
            async with self._model_lock:
                if self._model is None:
                    print(f"📥 Loading SpeechT5 TTS model: {self._model_name}")
                    print(f"   Device: {self._device}")
                    
                    try:
                        # Load processor and model
                        self._processor = SpeechT5Processor.from_pretrained(self._model_name)
                        self._model = SpeechT5ForTextToSpeech.from_pretrained(self._model_name)
                        self._model = self._model.to(self._device)
                        
                        # Load vocoder
                        self._vocoder = SpeechT5HifiGan.from_pretrained(self._vocoder_name)
                        self._vocoder = self._vocoder.to(self._device)
                        
                        # Get speaker embedding (default English female voice)
                        # According to SpeechT5 docs, speaker embeddings control voice characteristics
                        speaker_emb_dim = 512  # SpeechT5 speaker embedding dimension
                        self._speaker_emb = None
                        
                        try:
                            if self._speaker_embedding:
                                # Use provided embedding
                                if isinstance(self._speaker_embedding, str):
                                    # Try to load from dataset
                                    print(f"   Loading speaker embeddings from dataset...")
                                    try:
                                        embeddings_dataset = load_dataset(
                                            "Matthijs/cmu-arctic-xvectors",
                                            split="validation"
                                        )
                                        # Default: English female voice (index 7306)
                                        self._speaker_emb = torch.tensor(
                                            embeddings_dataset[7306]["xvector"]
                                        ).unsqueeze(0).to(self._device)
                                        print(f"   ✅ Loaded speaker embedding from dataset")
                                    except Exception as dataset_error:
                                        # Fallback: Use zero embedding (verified to work in test)
                                        print(f"   ⚠️  Dataset loading failed: {dataset_error}")
                                        print(f"   Using zero embedding (verified to work)")
                                        self._speaker_emb = torch.zeros(1, speaker_emb_dim).to(self._device)
                                else:
                                    # Pre-computed embedding provided
                                    self._speaker_emb = torch.tensor(
                                        self._speaker_embedding
                                    ).unsqueeze(0).to(self._device)
                            else:
                                # Use default speaker embedding from dataset
                                print(f"   Loading default speaker embedding...")
                                try:
                                    embeddings_dataset = load_dataset(
                                        "Matthijs/cmu-arctic-xvectors",
                                        split="validation"
                                    )
                                    # Default: English female voice (index 7306)
                                    self._speaker_emb = torch.tensor(
                                        embeddings_dataset[7306]["xvector"]
                                    ).unsqueeze(0).to(self._device)
                                    print(f"   ✅ Loaded default speaker embedding")
                                except Exception as dataset_error:
                                    # Fallback: Use zero embedding (verified to work in test)
                                    print(f"   ⚠️  Warning: Could not load speaker embeddings ({dataset_error})")
                                    print(f"   Using zero embedding (verified to work)")
                                    self._speaker_emb = torch.zeros(1, speaker_emb_dim).to(self._device)
                        except Exception as emb_error:
                            # Final fallback: Use zero embedding (tested and works)
                            print(f"   ⚠️  Final fallback: Using zero embedding")
                            self._speaker_emb = torch.zeros(1, speaker_emb_dim).to(self._device)
                        
                        if self._speaker_emb is None:
                            # Safety check: ensure we have an embedding
                            print(f"   ⚠️  Creating default embedding")
                            self._speaker_emb = torch.zeros(1, speaker_emb_dim).to(self._device)
                        
                        self._model.eval()
                        self._vocoder.eval()
                        
                        print(f"✅ TTS model loaded successfully")
                    except Exception as e:
                        print(f"❌ Failed to load TTS model: {e}")
                        import traceback
                        traceback.print_exc()
                        raise
    
    def synthesize(self, text: str, *, conn_options: Optional[object] = None) -> "tts.ChunkedStream":
        """Synthesize speech from text - non-async method that returns a stream"""
        # Return a stream that will handle the synthesis
        from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS
        conn_options = conn_options or DEFAULT_API_CONNECT_OPTIONS
        
        return SpeechT5TTSStream(
            tts=self,
            input_text=text,
            conn_options=conn_options,
        )


class SpeechT5TTSStream(tts.ChunkedStream):
    """Stream for SpeechT5 TTS synthesis - implements the ChunkedStream interface"""
    
    def __init__(
        self,
        *,
        tts: "SpeechT5TTSPlugin",
        input_text: str,
        conn_options: object,
    ):
        super().__init__(tts=tts, input_text=input_text, conn_options=conn_options)
        self._tts_plugin = tts
    
    async def _run(self, output_emitter: "tts.AudioEmitter") -> None:
        """
        Implement the actual synthesis logic.
        This is called by the ChunkedStream base class.
        """
        try:
            # Load the model (lazy loading)
            await self._tts_plugin._load_model()
            
            # Initialize the output emitter with audio format
            output_emitter.initialize(
                request_id=f"speecht5-{id(self)}",
                sample_rate=self._tts_plugin._sample_rate,
                num_channels=self._tts_plugin._num_channels,
                mime_type="audio/pcm",
            )
            
            loop = asyncio.get_event_loop()
            
            # Preprocess text
            inputs = await loop.run_in_executor(
                None,
                lambda: self._tts_plugin._processor(
                    text=self._input_text,
                    return_tensors="pt",
                )
            )
            
            # Move inputs to device
            inputs_device = {k: v.to(self._tts_plugin._device) for k, v in inputs.items()}
            
            # Generate speech
            with torch.no_grad():
                def generate():
                    return self._tts_plugin._model.generate_speech(
                        inputs_device["input_ids"],
                        self._tts_plugin._speaker_emb,
                        vocoder=self._tts_plugin._vocoder,
                    )
                
                speech = await loop.run_in_executor(None, generate)
            
            # Convert to numpy
            audio_data = speech.cpu().numpy().astype(np.float32)
            
            # Flatten if needed
            if len(audio_data.shape) > 1:
                audio_data = audio_data.flatten()
            
            # Apply speed adjustment by resampling if needed
            if abs(self._tts_plugin._speed - 1.0) > 0.01:  # Apply only if speed is different from 1.0
                # Speed adjustment: resample to change playback speed
                # Speed > 1.0: faster (fewer samples)
                # Speed < 1.0: slower (more samples)
                import scipy.signal
                num_samples = int(len(audio_data) / self._tts_plugin._speed)
                audio_data = scipy.signal.resample(audio_data, num_samples)
            
            # Normalize to [-1.0, 1.0] range
            max_val = np.abs(audio_data).max()
            if max_val > 0.0:
                audio_data = audio_data / max(1.0, max_val)
            
            # Convert to int16 for LiveKit (range: -32768 to 32767)
            audio_data = (audio_data * 32767.0).astype(np.int16)
            
            # Push audio data to output emitter as bytes
            # LiveKit's AudioEmitter expects bytes, not numpy arrays
            audio_bytes = audio_data.tobytes()
            output_emitter.push(audio_bytes)
            
        except Exception as e:
            print(f"❌ TTS synthesis error: {e}")
            import traceback
            traceback.print_exc()
            raise  # Let the ChunkedStream base class handle the error

# Alias for backward compatibility
CoquiTTSPlugin = SpeechT5TTSPlugin
