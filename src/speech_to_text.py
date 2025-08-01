# src/speech_to_text.py (Using Groq Whisper API + VAD)
import os
import io
import numpy as np
import pyaudio
import webrtcvad
from collections import deque
from scipy.io.wavfile import write as write_wav
from groq import Groq
from src.config import GROQ_API_KEY

# A comprehensive list of hints to guide Whisper's transcription
WHISPER_HINTS = "TAM-VA, Notepad, Chrome, VS Code, Aswin, Parthiban, Asin, Ai&Ds, volume, open, close, search, find, play, stop, email, Tamil, Tanglish, file, folder, weather, news, calculator, send, message, flirt with, chat with."

class SpeechToText:
    def __init__(self, model_size=None): # model_size is unused here, kept for consistency
        print("Initializing Groq Whisper Speech-to-Text...")
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in the .env file.")
        
        try:
            self.client = Groq(api_key=GROQ_API_KEY)
            print("Groq client initialized successfully.")
        except Exception as e:
            print(f"FATAL: Could not initialize Groq client. Error: {e}")
            self.client = None
        
        # VAD constants for capturing clean audio
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000 # Whisper is trained on 16kHz audio
        self.FRAME_DURATION_MS = 30
        self.CHUNK = int(self.RATE * self.FRAME_DURATION_MS / 1000)
        self.VAD_AGGRESSIVENESS = 3
        self.SILENCE_FRAMES_THRESHOLD = 35 # Stop after ~1 second of silence

    def _record_audio_with_vad(self):
        """
        Uses Voice Activity Detection (VAD) to record audio only when speech is detected.
        Returns the recorded audio as a NumPy array.
        """
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
                frames.append(data)
            
            if is_speaking and silent_frames_count > self.SILENCE_FRAMES_THRESHOLD:
                print("Silence detected, stopping recording.")
                break
        
        stream.stop_stream()
        stream.close()
        pa.terminate()

        # Combine frames into a single byte string
        audio_data = b"".join(list(frames))
        
        # Convert byte string to NumPy array
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        return audio_np

    def listen_and_transcribe(self):
        if not self.client:
            return "Speech-to-text service is not available."
            
        audio_np = self._record_audio_with_vad()

        if len(audio_np) < self.RATE / 2: # Ignore recordings less than 0.5s
            print("Recording too short, ignoring.")
            return ""

        # Create an in-memory WAV file from the NumPy array
        wav_bytes = io.BytesIO()
        write_wav(wav_bytes, self.RATE, (audio_np * 32767).astype(np.int16))
        wav_bytes.seek(0)
        # We need to give the in-memory file a name for the API
        wav_bytes.name = "recording.wav"

        print("Sending audio to Groq Cloud for transcription...")
        try:
            transcription = self.client.audio.transcriptions.create(
                file=("recording.wav", wav_bytes),
                model="whisper-large-v3",
                prompt=WHISPER_HINTS, # Provide contextual hints
                language="en"
            )
            
            print(f"Transcription: '{transcription.text}'")
            return transcription.text.strip()
            
        except Exception as e:
            print(f"Groq Whisper API error: {e}")
            return ""