import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")