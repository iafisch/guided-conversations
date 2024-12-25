import sounddevice as sd
import numpy as np
from typing import Optional

class AudioPlayer:
    """Simple audio playback handler"""
    def __init__(self, sample_rate: int = 24000):
        self.sample_rate = sample_rate
        self._stream = None

    def play_chunk(self, audio_data: bytes):
        """Play a chunk of audio data"""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Play audio
            sd.play(audio_array, self.sample_rate)
            sd.wait()  # Wait until audio is finished playing
        except Exception as e:
            print(f"Error playing audio: {e}") 