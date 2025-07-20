import pvporcupine
import pyaudio
import struct
from src.config import PICOVOICE_ACCESS_KEY

class WakeWordDetector:
    def __init__(self, keyword_path):
        self.access_key = PICOVOICE_ACCESS_KEY
        if not self.access_key:
            raise ValueError("PICOVOICE_ACCESS_KEY is not set in the .env file.")
        
        self.porcupine = pvporcupine.create(
            access_key=self.access_key,
            keyword_paths=[keyword_path]
        )
        self.pa = pyaudio.PyAudio()
        self.audio_stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

    def wait_for_wake_word(self):
        print(f"Listening for wake word...")
        while True:
            pcm = self.audio_stream.read(self.porcupine.frame_length)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            result = self.porcupine.process(pcm)
            if result >= 0:
                print("Wake word detected!")
                return True

    def __del__(self):
        if hasattr(self, 'porcupine') and self.porcupine is not None:
            self.porcupine.delete()
        if hasattr(self, 'audio_stream') and self.audio_stream is not None:
            self.audio_stream.close()
        if hasattr(self, 'pa') and self.pa is not None:
            self.pa.terminate()