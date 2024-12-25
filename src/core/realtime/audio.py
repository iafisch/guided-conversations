import base64
import numpy as np
import librosa
from typing import Optional

class RealtimeAudioProcessor:
    """Handles audio processing for Realtime API"""
    
    SAMPLE_RATE = 24000  # Must be 24kHz
    FORMAT = "pcm16"     # Must be PCM16
    
    def __init__(self):
        self.sample_rate = 24000
        self.format = "int16"  # PCM16
        self.channels = 1      # Mono required
        self.chunk_duration = 0.1  # 100ms chunks
        self.chunk_samples = int(self.sample_rate * self.chunk_duration)

    async def process_chunk(self, chunk: bytes) -> Optional[str]:
        """
        Process an audio chunk according to the specification:
          1) Convert the bytes to a numpy array (int16).
          2) Ensure the audio is mono.
          3) Resample if needed to match the required sample_rate.
          4) Convert back to bytes and encode base64 for sending to OpenAI Realtime.
        """
        audio = np.frombuffer(chunk, dtype=np.int16)

        if len(audio) == 0:
            return None
        
        # Ensure mono
        # If audio was multi-channel, average across channels
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)

        # Ideally, the length of audio in each chunk is chunk_size
        # If for some reason the chunk length is off, resample:
        if len(audio) != self.chunk_size:
            # libROSA resample requires float arrays
            audio_float = audio.astype(float)
            # We infer the original_sr from how many samples we got vs. expected chunk size
            original_sr = (len(audio) / self.chunk_size) * self.sample_rate
            # Resample to the correct sample_rate
            audio_resampled = librosa.resample(audio_float, orig_sr=original_sr, target_sr=self.sample_rate)
            # Convert back to int16
            audio = audio_resampled.astype(np.int16)

        # Encode to base64
        audio_bytes = audio.tobytes()
        return base64.b64encode(audio_bytes).decode('utf-8') 