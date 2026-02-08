# Voice Assistant

A Python-based intelligent voice assistant with advanced features including WhatsApp automation, Google Calendar integration, and web browser control. This voice assistant can perform various tasks through voice commands, making daily activities more efficient and hands-free.

## 🌟 Features

- **Voice Recognition**: Advanced speech-to-text capabilities using speech recognition
- **Text-to-Speech**: Natural-sounding voice responses
- **WhatsApp Automation**: Send messages and interact with WhatsApp through voice commands
- **Google Calendar Integration**: Manage calendar events, appointments, and reminders
- **Chrome Browser Control**: Automate web browsing tasks and searches
- **Voice Recording**: Capture and process voice commands with high accuracy
- **Multi-functional Commands**: Support for a wide range of tasks and queries

## 📁 Project Structure

```
voice-assistant/
├── src/                      # Source code modules
├── chrome_sessions/          # Chrome browser session data
├── whatsapp_user_data/       # WhatsApp user data and sessions
├── main.py                   # Main application entry point
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (API keys, credentials)
├── google_credentials.json   # Google API credentials
├── my_voice.wav             # Sample voice recording
├── temp_recording.wav       # Temporary audio file storage
└── .gitignore               # Git ignore rules
```

## 🛠️ Tech Stack

- **Language**: Python 100%
- **Speech Recognition**: Google Speech Recognition API
- **Text-to-Speech**: pyttsx3 / gTTS
- **Browser Automation**: Selenium WebDriver
- **Google APIs**: Google Calendar API, Google Cloud Speech-to-Text
- **WhatsApp**: WhatsApp Web automation
- **Audio Processing**: PyAudio, wave

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- pip package manager
- Google Chrome browser
- Microphone and speakers/headphones
- Active internet connection

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Parthiban1805/voice-assistant.git
cd voice-assistant
```

### 2. Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
# Google API Configuration
GOOGLE_API_KEY=your_google_api_key
GOOGLE_APPLICATION_CREDENTIALS=google_credentials.json

# OpenAI/Other AI APIs (if applicable)
OPENAI_API_KEY=your_openai_api_key

# Other Configuration
ASSISTANT_NAME=Jarvis
VOICE_RATE=150
```

### 4. Set Up Google Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Calendar API
   - Google Cloud Speech-to-Text API
4. Download the credentials JSON file
5. Rename it to `google_credentials.json` and place it in the root directory

### 5. Configure Chrome Driver

```bash
# Download ChromeDriver matching your Chrome version
# Place it in your system PATH or project directory
```

### 6. Run the Application

```bash
python main.py
```

## 🎤 Voice Commands

The assistant supports various voice commands:

### General Commands
- "Hello" / "Hi" - Greet the assistant
- "What's your name?" - Get assistant's name
- "What time is it?" - Get current time
- "What's the date?" - Get today's date
- "How are you?" - Check assistant status

### Web & Search
- "Search for [query]" - Google search
- "Open [website]" - Open specified website
- "Play [video] on YouTube" - Play YouTube videos
- "Wikipedia [topic]" - Get Wikipedia information

### Calendar & Reminders
- "Create calendar event" - Add new calendar event
- "List calendar events" - Show upcoming events
- "Delete calendar event" - Remove calendar event
- "Set reminder" - Create a reminder

### WhatsApp
- "Send WhatsApp message to [contact]" - Send WhatsApp message
- "Read WhatsApp messages" - Read recent messages

### System Commands
- "Exit" / "Quit" / "Stop" - Close the assistant
- "Take screenshot" - Capture screen
- "Open [application]" - Launch applications

## 🔧 Configuration

### Customizing Voice Settings

Edit the voice parameters in `main.py`:

```python
# Voice rate (speed)
engine.setProperty('rate', 150)

# Voice volume (0.0 to 1.0)
engine.setProperty('volume', 0.9)

# Voice selection (male/female)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 0 for male, 1 for female
```

### Adding Custom Commands

You can extend the assistant by adding custom commands in the `src/` directory or modifying `main.py`:

```python
def custom_command(query):
    if 'custom trigger' in query:
        # Your custom logic here
        speak("Executing custom command")
        # Add your functionality
```

## 📝 Requirements

Key Python packages (see `requirements.txt` for complete list):

```
SpeechRecognition
pyttsx3
pyaudio
selenium
google-api-python-client
google-auth-oauthlib
pywhatkit
wikipedia
requests
python-dotenv
```

## 🐛 Troubleshooting

### Microphone Issues
- Ensure your microphone is properly connected
- Check system permissions for microphone access
- Test microphone with: `python -m speech_recognition`

### Google API Errors
- Verify `google_credentials.json` is properly configured
- Ensure required APIs are enabled in Google Cloud Console
- Check internet connection

### WhatsApp Connection
- Make sure WhatsApp Web is accessible
- Scan QR code when prompted
- Check `whatsapp_user_data/` for session data

### Chrome Driver Issues
- Ensure ChromeDriver version matches your Chrome browser
- Update ChromeDriver if needed
- Check PATH configuration

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🔒 Security & Privacy

- **Never commit** `.env`, `google_credentials.json`, or any sensitive data
- Keep your API keys secure and private
- Review `.gitignore` before committing
- User data is stored locally and not shared

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Parthiban**
- GitHub: [@Parthiban1805](https://github.com/Parthiban1805)

## 🙏 Acknowledgments

- Google Cloud Platform for Speech and Calendar APIs
- OpenAI for potential AI integration
- Python Speech Recognition community
- Selenium WebDriver contributors
- All open-source libraries used in this project

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Contact the maintainer

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Smart home device integration
- [ ] Email management capabilities
- [ ] Weather and news updates
- [ ] Custom wake word detection
- [ ] Offline mode support
- [ ] Mobile app integration
- [ ] Voice authentication
- [ ] Context-aware conversations
- [ ] Task automation workflows

## ⚠️ Important Notes

1. **First Run**: The assistant may prompt for various permissions (microphone, browser access, etc.)
2. **Google Login**: You'll need to authenticate Google services on first use
3. **WhatsApp Setup**: Scan QR code to link WhatsApp Web
4. **Audio Quality**: Use a good quality microphone for better recognition accuracy
5. **Background Noise**: Minimize background noise for optimal performance

## 🎯 Use Cases

- **Productivity**: Hands-free calendar and task management
- **Accessibility**: Assistance for users with physical limitations
- **Automation**: Automate repetitive web and messaging tasks
- **Information**: Quick access to information through voice
- **Communication**: Voice-controlled messaging and notifications

---

**Note**: This is a personal voice assistant project. For production use, ensure proper error handling, security measures, and compliance with relevant data protection regulations.

