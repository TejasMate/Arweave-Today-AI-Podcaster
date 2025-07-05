# 🎙️ Arweave Today AI Podcaster

An intelligent, automated podcast generator that transforms Arweave ecosystem news into professional-quality audio content. This tool fetches the latest news from the Arweave Today feed, transcribes video content, enhances scripts with AI, and generates natural-sounding podcast audio.

## ✨ Features

### 🤖 AI-Powered Content Enhancement
- **Gemini AI Script Generation**: Transforms raw news content into professional, conversational podcast scripts
- **Natural Voice Optimization**: Optimizes text for natural "Puck" voice personality with TTS enhancements
- **Topic Separation**: Automatically organizes content with clear topic boundaries for AI processing

### 🎥 Video Content Processing
- **YouTube Video Transcription**: Downloads and transcripts embedded videos using Whisper AI
- **Smart Caching**: Avoids re-processing existing transcripts to save time and bandwidth
- **Error Handling**: Graceful fallback when video processing fails

### 🌐 Flexible Data Sources
- **Online Fetching**: Retrieves latest content from `today_arweave.ar.io`
- **Local Fallback**: Uses local JSON files when online source is unavailable
- **Smart SSL Handling**: Handles certificate issues automatically
- **Multiple Endpoint Support**: Tries various JSON endpoints for robust data retrieval

### 🎵 Professional Audio Generation
- **Gemini-Enhanced TTS**: Uses AI-optimized text for natural speech synthesis
- **Speaker Diarization**: Optional AssemblyAI speaker analysis for generated audio
- **Multiple Output Formats**: Generates both raw and enhanced scripts plus final audio

### 🔧 Developer-Friendly
- **Environment Configuration**: Secure API key management with `.env` files
- **Modular Architecture**: Clean, maintainable code structure
- **Comprehensive Logging**: Detailed progress tracking and error reporting
- **Easy Customization**: Configurable models, voices, and processing options

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FFmpeg (for audio processing)
- API keys for Gemini AI and AssemblyAI (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/arweave-today-ai-podcaster.git
   cd arweave-today-ai-podcaster
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the generator**
   ```bash
   cd src
   python podcast_generator.py
   ```

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# API Keys
ASSEMBLYAI_API_KEY=your_assemblyai_key_here
GEMINI_API_KEY=your_gemini_key_here

# Feature Toggles
ENABLE_ASSEMBLYAI_DIARIZATION=True
ENABLE_GEMINI_SCRIPT_GENERATION=True

# Optional Settings
FFMPEG_PATH=
WHISPER_MODEL=tiny.en
```

### API Key Setup

#### Google Gemini AI (Required for AI Enhancement)
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Add to `.env` as `GEMINI_API_KEY`

#### AssemblyAI (Optional for Speaker Diarization)
1. Sign up at [AssemblyAI](https://www.assemblyai.com/)
2. Get your API key from dashboard
3. Add to `.env` as `ASSEMBLYAI_API_KEY`

## 📊 Data Source Options

When running the script, you'll be prompted to choose a data source:

1. **🌐 Online** - Fetch latest from today_arweave.ar.io
2. **📁 Local** - Use local `data/today.json` file
3. **🔄 Auto** - Try online first, fallback to local (recommended)

## 📁 Project Structure

```
arweave-today-ai-podcaster/
├── src/
│   ├── podcast_generator.py    # Main application
│   └── test_gemini.py         # Testing utilities
├── data/
│   ├── today.json             # Local news data
│   └── today_backup.json      # Auto-saved backup
├── output/                    # Generated content
│   ├── ArweaveToday-YYYY-MM-DD-raw.txt
│   ├── ArweaveToday-YYYY-MM-DD.txt
│   ├── ArweaveToday-YYYY-MM-DD.mp3
│   └── topic_*_video_transcript.txt
├── .env                       # API configuration
├── .env.example              # Configuration template
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🎯 Output Files

### Generated Content
- **Raw Script** (`*-raw.txt`) - Combined news and video transcripts with topic markers
- **Enhanced Script** (`*.txt`) - AI-polished, professional podcast script
- **Audio File** (`*.mp3`) - Final podcast audio with natural Puck voice
- **Video Transcripts** (`topic_*_transcript.txt`) - Individual video transcriptions

### File Naming Convention
All output files use the format: `ArweaveToday-YYYY-MM-DD.*`

## 🔍 Features Deep Dive

### AI Script Enhancement
The Gemini AI processor transforms raw content into professional podcast scripts by:
- Creating natural, conversational flow
- Adding clear transitions between topics
- Explaining technical terms accessibly
- Maintaining enthusiastic but professional tone
- Optimizing for audio delivery

### Voice Personality: "Puck"
The AI optimizes scripts for a friendly, enthusiastic tech podcaster named "Puck":
- Conversational and warm tone
- Natural speech patterns
- Professional but approachable delivery
- Uses natural filler words occasionally
- Explains concepts like talking to a friend

### Smart Video Processing
- Downloads audio from embedded YouTube videos
- Transcribes using Whisper AI (configurable models)
- Saves individual transcripts per topic
- Skips re-processing existing transcripts
- Handles errors gracefully with fallback content

## 🛠️ Advanced Configuration

### Whisper Model Options
Set `WHISPER_MODEL` in `.env`:
- `tiny.en` - Fastest, least accurate (default)
- `base.en` - Good balance of speed/accuracy
- `small.en` - Better accuracy, slower
- `medium.en` - Best accuracy, slowest

### FFmpeg Configuration
If FFmpeg is not in your system PATH:
1. Download FFmpeg from [official site](https://ffmpeg.org/)
2. Set `FFMPEG_PATH` to the `bin` directory in `.env`

## 🧪 Testing

Test individual components:

```bash
# Test Gemini AI integration
python test_gemini.py

# Test with local data only
python podcast_generator.py
# Choose option 2 (Local)
```

## 🐛 Troubleshooting

### Common Issues

**SSL Certificate Errors**
- The script automatically handles SSL issues with fallback mechanisms
- No action required from user

**Missing FFmpeg**
- Install FFmpeg and add to PATH, or set `FFMPEG_PATH` in `.env`

**API Key Issues**
- Verify keys are correctly set in `.env`
- Check API key permissions and quotas

**Video Transcription Fails**
- Script continues with text-only content
- Check network connectivity for video downloads

### Debug Mode
Add verbose logging by modifying the script or check output files for detailed error information.

## 📝 Dependencies

### Core Dependencies
- `gTTS==2.5.1` - Text-to-speech generation
- `yt-dlp==2024.7.16` - Video downloading
- `faster-whisper==1.0.3` - Speech-to-text transcription
- `google-generativeai` - Gemini AI integration
- `requests==2.31.0` - HTTP requests
- `python-dotenv==1.0.0` - Environment variable management

### Optional Dependencies
- `pydub==0.25.1` - Audio processing utilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔒 Security

- API keys are stored in `.env` files (not committed to version control)
- `.gitignore` includes sensitive files
- Use environment variables for all configuration
- Regular dependency updates recommended

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Arweave Team** - For the innovative permanent storage ecosystem
- **Google Gemini AI** - For natural language processing capabilities
- **AssemblyAI** - For speaker diarization services
- **OpenAI Whisper** - For accurate speech transcription
- **Community Contributors** - For feedback and improvements

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/arweave-today-ai-podcaster/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/arweave-today-ai-podcaster/discussions)
- **Email**: your-email@example.com

---

Made with ❤️ for the Arweave ecosystem. Building the permanent web, one podcast at a time.
