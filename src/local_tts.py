# src/local_tts.py (Corrected version 4 - Final)
import torch
import sounddevice as sd
import numpy as np
import json # <--- Import the JSON library
from TTS.api import TTS
from piper.voice import PiperVoice

class LocalTTS:
    def __init__(self):
        print("Initializing Local TTS Engines...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        # --- Initialize Coqui XTTS (Primary Voice) ---
        print("Loading Coqui XTTS model...")
        try:
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
            self.primary_voice = TTS(model_name).to(self.device)
            self.speaker_wav_path = "my_voice.wav"
            print("Coqui XTTS model loaded successfully.")
        except Exception as e:
            print(f"Could not load Coqui TTS model. Primary voice will be disabled. Error: {e}")
            self.primary_voice = None

        # --- Initialize Piper (Feedback Voice) ---
        print("Loading Piper feedback voice model...")
        try:
            # THIS IS THE DEFINITIVE FIX FOR PIPER
            model_path = r"P:\development\voice assistant\src\piper_models"
            config_path = f"{model_path}.json"
            
            # 1. Load the config JSON file into a dictionary
            with open(config_path, "r") as f:
                config_data = json.load(f)
            
            # 2. Pass the model path and the loaded config dictionary
            self.feedback_voice = PiperVoice(model_path, config=config_data)
            
            if self.device == "cuda":
                self.feedback_voice.to(self.device)
            print("Piper model loaded successfully.")
        except Exception as e:
            print(f"Could not load Piper model. Feedback voice will be disabled. Error: {e}")
            self.feedback_voice = None

    def _play_audio(self, audio_data, sample_rate):
        sd.play(np.frombuffer(audio_data, dtype=np.int16), samplerate=sample_rate)
        sd.wait()

    def speak_primary(self, text: str, language: str = "en"):
        if not self.primary_voice:
            print("Primary voice is not available.")
            self.speak_feedback("My main voice is currently unavailable.")
            return
        print(f"Speaking (Coqui XTTS): {text}")
        try:
            wav_out = self.primary_voice.tts(text=text, speaker_wav=self.speaker_wav_path, language=language, split_sentences=True)
            sd.play(np.array(wav_out), samplerate=24000)
            sd.wait()
        except Exception as e:
            print(f"Error during Coqui TTS generation: {e}")
            self.speak_feedback("I encountered an error with my voice synthesis.")

    def speak_feedback(self, text: str):
        if not self.feedback_voice:
            print(f"Feedback voice not available. Cannot speak: '{text}'")
            return
        print(f"Speaking (Piper): {text}")
        try:
            audio_bytes = b"".join(self.feedback_voice.synthesize(text))
            self._play_audio(audio_bytes, self.feedback_voice.config.sample_rate)
        except Exception as e:
            print(f"Error during Piper TTS generation: {e}")