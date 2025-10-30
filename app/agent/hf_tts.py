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
    ):
        """
        Initialize SpeechT5 TTS
        
        Args:
            model: TTS model name from Hugging Face
            vocoder: Vocoder model name (converts features to audio)
            speaker_embedding: Pre-computed speaker embedding or dataset name
            device: Device to run on ("cpu", "cuda"). Auto-detected if None
        """
        super().__init__(
            sample_rate=16000,  # SpeechT5 default sample rate
            num_channels=1,
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
                        if self._speaker_embedding:
                            # Use provided embedding
                            if isinstance(self._speaker_embedding, str):
                                # Try to load from dataset
                                embeddings_dataset = load_dataset(
                                    "Matthijs/cmu-arctic-xvectors",
                                    split="validation"
                                )
                                self._speaker_emb = torch.tensor(
                                    embeddings_dataset[7306]["xvector"]
                                ).unsqueeze(0).to(self._device)
                            else:
                                self._speaker_emb = torch.tensor(
                                    self._speaker_embedding
                                ).unsqueeze(0).to(self._device)
                        else:
                            # Use default speaker embedding
                            embeddings_dataset = load_dataset(
                                "Matthijs/cmu-arctic-xvectors",
                                split="validation"
                            )
                            # Default: English female voice (index 7306)
                            self._speaker_emb = torch.tensor(
                                embeddings_dataset[7306]["xvector"]
                            ).unsqueeze(0).to(self._device)
                        
                        self._model.eval()
                        self._vocoder.eval()
                        
                        print(f"✅ TTS model loaded successfully")
                    except Exception as e:
                        print(f"❌ Failed to load TTS model: {e}")
                        import traceback
                        traceback.print_exc()
                        raise
    
    async def synthesize(self, text: str, fnc_ctx: Optional[object] = None) -> "tts.SynthesizeStream":
        """Synthesize speech from text"""
        await self._load_model()
        
        # Create a stream
        stream = SpeechT5TTSStream(
            self._processor,
            self._model,
            self._vocoder,
            self._speaker_emb,
            text,
            self.sample_rate,
            self._device,
        )
        
        return stream


class SpeechT5TTSStream(tts.SynthesizeStream):
    """Stream for SpeechT5 TTS synthesis"""
    
    def __init__(
        self,
        processor: SpeechT5Processor,
        model: SpeechT5ForTextToSpeech,
        vocoder: SpeechT5HifiGan,
        speaker_emb: torch.Tensor,
        text: str,
        sample_rate: int,
        device: str,
    ):
        super().__init__()
        self._processor = processor
        self._model = model
        self._vocoder = vocoder
        self._speaker_emb = speaker_emb
        self._text = text
        self._sample_rate = sample_rate
        self._device = device
        self._synthesized = False
    
    async def __aiter__(self) -> AsyncIterator[rtc.AudioFrame]:
        """Generate audio frames"""
        if self._synthesized:
            return
        
        self._synthesized = True
        
        try:
            # Run TTS in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            
            # Preprocess text
            inputs = await loop.run_in_executor(
                None,
                self._processor,
                text=self._text,
                return_tensors="pt",
            )
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            # Generate speech
            with torch.no_grad():
                # Generate speech features
                speech = await loop.run_in_executor(
                    None,
                    lambda: self._model.generate_speech(
                        inputs["input_ids"],
                        self._speaker_emb,
                        vocoder=self._vocoder,
                    )
                )
            
            # Convert to numpy
            audio_data = speech.cpu().numpy().astype(np.float32)
            
            # Normalize to [-1.0, 1.0] range
            max_val = np.abs(audio_data).max()
            if max_val > 1.0:
                audio_data = audio_data / max_val
            
            # Ensure sample rate matches
            actual_sr = self._sample_rate
            if actual_sr != self._sample_rate:
                # Resample if needed
                from scipy import signal
                num_samples = int(len(audio_data) * self._sample_rate / actual_sr)
                audio_data = signal.resample(audio_data, num_samples)
            
            # Convert to int16
            audio_data = (audio_data * 32767.0).astype(np.int16)
            
            # Split into chunks for streaming
            chunk_size = int(self._sample_rate * 0.1)  # 100ms chunks
            
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                
                # Ensure chunk is the right size (pad if necessary)
                if len(chunk) < chunk_size:
                    padded_chunk = np.zeros(chunk_size, dtype=np.int16)
                    padded_chunk[:len(chunk)] = chunk
                    chunk = padded_chunk
                
                # Create audio frame
                audio_frame = rtc.AudioFrame(
                    data=chunk.reshape(1, -1).tobytes(),
                    sample_rate=self._sample_rate,
                    num_channels=1,
                    samples_per_channel=len(chunk),
                )
                
                yield audio_frame
                
                # Small delay to simulate real-time streaming
                await asyncio.sleep(0.05)
                
        except Exception as e:
            print(f"❌ TTS synthesis error: {e}")
            import traceback
            traceback.print_exc()
            # Return empty frame on error
            empty_frame = rtc.AudioFrame(
                data=np.zeros(self._sample_rate // 10, dtype=np.int16).tobytes(),
                sample_rate=self._sample_rate,
                num_channels=1,
                samples_per_channel=self._sample_rate // 10,
            )
            yield empty_frame

# Alias for backward compatibility
CoquiTTSPlugin = SpeechT5TTSPlugin
