# 🎙️ Arweave Today AI Podcaster

An intelligent, automated podcast generator that transforms Arweave ecosystem news into professional-quality audio content. This tool fetches the latest news from the Arweave Today feed, transcribes video content, enhances scripts with AI, and generates natural-sounding podcast audio.

## 🎧 Sample Generated Podcast

Here's an example of what the AI generates - listen to how it transforms raw news into a natural, conversational podcast:

https://github.com/user-attachments/assets/1cabd7e0-a61d-401c-a698-4669f3916abc

**What you'll hear:**
- 🎙️ Natural "Puck" voice personality
- 📰 Latest Arweave ecosystem news
- 🎯 Professional transitions between topics
- 💡 Technical concepts explained accessibly
- ⚡ Generated entirely by AI in minutes

## ✨ Features

### 🤖 AI-Powered Content Enhancement
- **Gemini AI Script Generation**: Transforms raw news content into professional, conversational podcast scripts
- **Natural Voice Optimization**: Optimizes text for natural "Puck" voice personality with TTS enhancements
- **Topic Separation**: Automatically organizes content with clear topic boundaries for AI processing

### 🎥 Video Content Processing
- **YouTube Video Transcription**: Downloads and transcripts embedded videos using Gemini AI
- **Smart Caching**: Avoids re-processing existing transcripts to save time and bandwidth
- **Error Handling**: Graceful fallback when video processing fails

### 🌐 Flexible Data Sources
- **Online Fetching**: Retrieves latest content from `today_arweave.ar.io`
- **Local Fallback**: Uses local JSON files when online source is unavailable
- **Smart SSL Handling**: Handles certificate issues automatically
- **Multiple Endpoint Support**: Tries various JSON endpoints for robust data retrieval

### 🎵 Professional Audio Generation
- **Gemini TTS**: Uses AI-optimized text for natural speech synthesis with "Puck" voice
- **Structured Transcription**: Audio-to-text transcription with timestamps and speaker identification
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
- API key for Gemini AI

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/arweave-today-ai-podcaster.git
   cd arweave-today-ai-podcaster
   ```

2. **Install the package**
   ```bash
   # Standard installation
   pip install -r requirements.txt
   
   # OR development installation (recommended for contributors)
   pip install -e .
   pip install -e .[dev]  # Include development dependencies
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the generator**
   ```bash
   python main.py
   
   # OR if installed as package
   arweave-podcaster
   
   # OR as module
   python -m arweave_podcaster.core.podcast_generator
   ```

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# API Keys
GEMINI_API_KEY=your_gemini_key_here

# Feature Toggles
ENABLE_GEMINI_SCRIPT_GENERATION=True
ENABLE_GEMINI_TTS=True

# Optional Settings
FFMPEG_PATH=
```

### API Key Setup

#### Google Gemini AI (Required)
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Add to `.env` as `GEMINI_API_KEY`

## 📊 Data Source Options

When running the script, you'll be prompted to choose a data source:

1. **🌐 Online** - Fetch latest from today_arweave.ar.io
2. **📁 Local** - Use local `data/today.json` file
3. **🔄 Auto** - Try online first, fallback to local (recommended)

## 📁 Project Structure

```
arweave-today-ai-podcaster/
├── arweave_podcaster/              # Main package
│   ├── __init__.py                # Package initialization  
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   └── podcast_generator.py   # Main podcast generator
│   ├── services/                  # External service integrations
│   │   ├── __init__.py
│   │   ├── data_service.py        # News data fetching
│   │   ├── gemini_service.py      # Gemini AI integration
│   │   └── video_service.py       # Video transcription
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── audio_utils.py         # Audio processing
│       ├── config.py              # Configuration management
│       ├── file_utils.py          # File operations
│       └── text_utils.py          # Text processing
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_config.py
│   └── test_text_utils.py
├── scripts/                       # Utility scripts
│   └── setup_dev.sh               # Development setup
├── docs/                          # Documentation
│   ├── api_reference.md           # API documentation
│   └── development.md             # Development guide
├── data/                          # Data storage (by date)
│   └── DD-MM-YYYY/
│       └── today.json
├── output/                        # Generated content (by date)
│   └── DD-MM-YYYY/
│       ├── ArweaveToday-YYYY-MM-DD-raw.txt
│       ├── ArweaveToday-YYYY-MM-DD.txt
│       ├── ArweaveToday-YYYY-MM-DD.wav
│       └── topic_*_video_transcript.txt
├── main.py                        # CLI entry point
├── setup.py                       # Package setup (legacy)
├── pyproject.toml                 # Modern packaging config
├── requirements.txt               # Dependencies
├── .env                           # Environment configuration
├── .env.example                   # Configuration template
└── README.md                      # This file
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
- Transcribes using Gemini AI with structured timestamps and speaker identification
- Saves individual transcripts per topic
- Skips re-processing existing transcripts
- Handles errors gracefully with fallback content

## 🛠️ Advanced Configuration

### FFmpeg Configuration
If FFmpeg is not in your system PATH:
1. Download FFmpeg from [official site](https://ffmpeg.org/)
2. Set `FFMPEG_PATH` to the `bin` directory in `.env`

## 🧪 Testing

The main script includes built-in API testing:

```bash
# Run with built-in API testing
python main.py
# The script automatically tests Gemini AI connections

# Test with local data only
python main.py
# Choose option 2 (Local) when prompted
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
- `google-generativeai` - Gemini AI integration for TTS and transcription
- `yt-dlp==2024.7.16` - Video downloading
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
- **Google Gemini AI** - For natural language processing, TTS, and transcription capabilities
- **OpenAI** - For inspiration in AI-powered content generation
- **Community Contributors** - For feedback and improvements

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/tejasmate/arweave-today-ai-podcaster/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tejasmate/arweave-today-ai-podcaster/discussions)
- **Email**: tejasmate@zoho.com

---

Made with ❤️ for the Arweave ecosystem. Building the permanent web, one podcast at a time.

## 🚀 Upcoming Features

### 🎤 Enhanced Voice Models
- **Advanced TTS Integration**: Voice model may be upgraded soon for even more natural speech synthesis
- **Multiple Voice Options**: Planning to support different voice personalities beyond "Puck"
- **Improved Audio Quality**: Enhanced processing for professional-grade podcast audio

### 🐦 Social Media Integration
- **X/Twitter Post Scraping**: Automatic collection of relevant Arweave ecosystem tweets and discussions
- **Community Sentiment**: Integration of social media buzz and community reactions
- **Real-time Social Updates**: Incorporation of breaking news from social platforms

### 📰 Extended Content Sources
- **Website Article Scraping**: Automatic extraction from Arweave-related blogs and news sites
- **Documentation Updates**: Integration of official Arweave documentation changes
- **Research Paper Summaries**: AI-powered summaries of academic papers and technical documents
- **Enhanced Context**: Richer podcast content with broader ecosystem coverage

### 🔮 Content Intelligence
- **Contextual Linking**: Smart connections between related topics across different sources
- **Trend Analysis**: AI-powered identification of emerging trends in the Arweave ecosystem
- **Personalized Content**: Customizable focus areas based on listener preferences

*These features are in active development. Stay tuned for updates!*

## 🚀 Quick Start
