# src/speech_to_text.py
import whisper
import numpy as np
import pyaudio
import webrtcvad
from collections import deque

# A comprehensive list of hints to guide Whisper's transcription
WHISPER_HINTS = "TAM-VA, Notepad, Chrome, VS Code, volume, open, close, search, find, play, stop, email, Tamil, Tanglish, file, folder, weather, news, calculator, send, message."

class SpeechToText:
    def __init__(self, model_size="small"): # Default to the more accurate 'small' model
        print(f"Loading Whisper model '{model_size}'...")
        self.model = whisper.load_model(model_size)
        print("Whisper model loaded.")
        
        # VAD constants for capturing clean audio
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.FRAME_DURATION_MS = 30
        self.CHUNK = int(self.RATE * self.FRAME_DURATION_MS / 1000)
        self.VAD_AGGRESSIVENESS = 3
        self.SILENCE_FRAMES_THRESHOLD = 35 # Stop after ~1 second of silence

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
            if vad.is_speech(data, self.RATE):
                if not is_speaking:
                    print("Speech detected...")
                is_speaking = True
                silent_frames_count = 0
                frames.append(data)
            elif is_speaking:
                silent_frames_count += 1
                frames.append(data) # Also capture a bit of silence at the end
            
            if is_speaking and silent_frames_count > self.SILENCE_FRAMES_THRESHOLD:
                print("Silence detected, stopping recording.")
                break
        
        stream.stop_stream()
        stream.close()
        pa.terminate()

        audio_data = b"".join(list(frames))
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        if len(audio_np) < self.RATE / 2: # Ignore recordings less than 0.5s
            print("Recording too short, ignoring.")
            return ""

        result = self.model.transcribe(audio_np, language='en', initial_prompt=WHISPER_HINTS)
        print(f"Raw Transcription: '{result['text']}'")
        return result['text'].strip()