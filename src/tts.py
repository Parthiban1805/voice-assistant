# src/tts.py

from elevenlabs.client import ElevenLabs # Correct import for new version
from elevenlabs import play
from src.config import ELEVENLABS_API_KEY
import os

class TextToSpeech:
    def __init__(self):
        if not ELEVENLABS_API_KEY:
            raise ValueError("ELEVENLABS_API_KEY is not set in .env file.")
        # Correct client initialization for new version
        self.client = ElevenLabs(api_key=ELEVENLABS_API_KEY) 
        self.cloned_voice_id = "EXAVITQu4vr4xnSDxMaL" # Your Voice ID

    def speak_primary(self, text):
        """Uses high-quality ElevenLabs voice for main responses."""
        print(f"Speaking (ElevenLabs): {text}")
        try:
            # This line will now work correctly
            audio = self.client.tts.generate(
                text=text,
                voice=self.cloned_voice_id,
                model="eleven_multilingual_v2"
            )
            play(audio)
        except Exception as e:
            print(f"Error with ElevenLabs: {e}")
            self.speak_feedback("I encountered an error with my voice synthesis.")

    def speak_feedback(self, text):
        """Uses a simple local method for quick feedback."""
        print(f"Speaking (Local Feedback): {text}")
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except ImportError:
            print("pyttsx3 not installed, cannot provide local feedback.")