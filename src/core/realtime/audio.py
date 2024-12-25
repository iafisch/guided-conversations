import base64
import numpy as np
import librosa
from typing import Optional
import sounddevice as sd  # For audio playback

class RealtimeAudioProcessor:
    """Handles audio processing for Realtime API"""
    
    SAMPLE_RATE = 24000  # Must be 24kHz
    FORMAT = "pcm16"     # Must be PCM16
    
    def __init__(self):
        self.sample_rate = 24000
        self.channels = 1
        self.chunk_duration = 0.1  # 100ms chunks
        self.chunk_samples = int(self.sample_rate * self.chunk_duration)

    async def process_chunk(self, chunk: bytes) -> Optional[bytes]:
        """Process input audio chunk"""
        try:
            # Convert to numpy array
            audio = np.frombuffer(chunk, dtype=np.int16)
            
            # Ensure mono
            if len(audio.shape) > 1:
                audio = audio.mean(axis=1).astype(np.int16)
            
            # Ensure correct sample rate
            if len(audio) != self.chunk_samples:
                audio = librosa.resample(
                    audio,
                    orig_sr=len(audio) / self.chunk_duration,
                    target_sr=self.sample_rate
                ).astype(np.int16)
            
            return audio.tobytes()
            
        except Exception as e:
            print(f"Error processing audio chunk: {e}")
            return None
            
    async def process_output_chunk(self, chunk: bytes):
        """Process output audio chunk from the API"""
        # The API sends PCM16 audio that can be played directly
        # Implement audio playback here if needed
        pass 