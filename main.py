import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play

# Load API key
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
MY_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"

print("--- ElevenLabs v2.7 Test ---")

if not ELEVENLABS_API_KEY:
    print("ERROR: ELEVENLABS_API_KEY not found in .env file.")
else:
    try:
        print("Initializing ElevenLabs client...")
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

        # ✅ This is the CORRECT method for v2.7
        audio = client.text_to_speech.convert(
            voice_id=MY_VOICE_ID,
            text="This is a test of the Eleven Labs API.",
            model_id="eleven_multilingual_v2"
        )

        print("Audio generated. Playing...")
        play(audio)

    except Exception as e:
        print("--- ERROR ---")
        print(f"{type(e).__name__}: {e}")
