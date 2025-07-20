# src/speech_to_text.py (NEW - with Voice Activity Detection)
import whisper
import numpy as np
import pyaudio
import webrtcvad
from collections import deque
import wave

WHISPER_HINTS = "TAM-VA, Notepad, Chrome, VS Code, volume, open, close, search, find, play, stop, email, Tamil, Tanglish, file, folder, weather, news."

class SpeechToText:
    def __init__(self, model_size="small"):
        print(f"Loading Whisper model '{model_size}'...")
        self.model = whisper.load_model(model_size)
        print("Whisper model loaded.")
        
        # VAD constants
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.FRAME_DURATION_MS = 30  # VAD supports 10, 20, or 30 ms
        self.CHUNK = int(self.RATE * self.FRAME_DURATION_MS / 1000)
        self.VAD_AGGRESSIVENESS = 3 # 0 to 3 (most aggressive)
        self.SILENCE_FRAMES_THRESHOLD = 35 # ~1 second of silence to stop

    def listen_and_transcribe(self):
        print("Listening for command (VAD enabled)...")
        vad = webrtcvad.Vad(self.VAD_AGGRESSIVENESS)
        pa = pyaudio.PyAudio()
        stream = pa.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        
        frames = deque()
        is_speaking = False
        silent_frames_count = 0
        
        while True:
            data = stream.read(self.CHUNK)
            frames.append(data)
            if vad.is_speech(data, self.RATE):
                is_speaking = True
                silent_frames_count = 0
            elif is_speaking:
                silent_frames_count += 1
            
            # If we've been speaking and then go silent for a period, stop.
            if is_speaking and silent_frames_count > self.SILENCE_FRAMES_THRESHOLD:
                break
        
        # Cleanup
        stream.stop_stream()
        stream.close()
        pa.terminate()

        # Combine frames and transcribe
        audio_data = b"".join(list(frames))
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        if len(audio_np) < 1000: # Not enough audio to be a command
            print("No significant command detected.")
            return ""

        result = self.model.transcribe(audio_np, language='en', initial_prompt=WHISPER_HINTS)
        print(f"Transcription: {result['text']}")
        return result['text'].strip()