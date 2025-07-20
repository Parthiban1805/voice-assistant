import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

class SpeechToText:
    def __init__(self, model_size="base"):
        print(f"Loading Whisper model '{model_size}'...")
        self.model = whisper.load_model(model_size)
        print("Whisper model loaded.")
        self.samplerate = 16000  # Whisper's required sample rate

    def listen_and_transcribe(self, duration=5):
        print("Listening for command...")
        recording = sd.rec(int(duration * self.samplerate), samplerate=self.samplerate, channels=1, dtype='float32')
        sd.wait()  # Wait for recording to finish

        # Check if the recording is mostly silent
        if np.max(np.abs(recording)) < 0.02: # Silence threshold
            print("No significant audio detected.")
            return ""

        # Transcribe
        result = self.model.transcribe(recording.flatten(), language='en') # Specify language to help with Tanglish
        print(f"Transcription: {result['text']}")
        return result['text'].strip()