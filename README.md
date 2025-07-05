# 🎙️ Arweave Today AI Podcaster

An intelligent, automated podcast generator that transforms Arweave ecosystem news into professional-quality audio content. This tool fetches the latest news from the Arweave Today feed, transcribes video content, enhances scripts with AI, and generates natural-sounding podcast audio.

## 📺 Demo & Examples

### Web Interface Demo
https://github.com/user-attachments/assets/49f7d38e-46d8-4c2c-bbe6-96aaec5a4daf

### 🎧 Sample Generated Podcast
Here's an example of what the AI generates - listen to how it transforms raw news into a natural, conversational podcast:

https://github.com/user-attachments/assets/1cabd7e0-a61d-401c-a698-4669f3916abc

**What you'll hear:**
- 🎙️ Natural "Puck" voice personality
- 📰 Latest Arweave ecosystem news
- 🎯 Professional transitions between topics
- 💡 Technical concepts explained accessibly
- ⚡ Generated entirely by AI in minutes

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

3. **Install FFmpeg (Required for audio processing)**

   **On Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

   **On macOS (with Homebrew):**
   ```bash
   brew install ffmpeg
   ```

   **On Windows:**
   - Download FFmpeg from [official website](https://ffmpeg.org/download.html)
   - Extract to a folder (e.g., `C:\ffmpeg`)
   - Add `C:\ffmpeg\bin` to your system PATH
   - OR set `FFMPEG_PATH=C:\ffmpeg\bin` in your `.env` file

   **Verify Installation:**
   ```bash
   ffmpeg -version
   ```
   You should see FFmpeg version information if installed correctly.

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the generator**
   
   **Command Line Interface:**
   ```bash
   python main.py
   
   # OR if installed as package
   arweave-podcaster
   
   # OR as module
   python -m arweave_podcaster.core.podcast_generator
   ```
   
   **Web Interface (Recommended for beginners):**
   ```bash
   python web_app.py
   # Then open http://localhost:5000 in your browser
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

## 🎮 Usage

### 🌐 Web Interface (Recommended)
Access the modern web interface for easy podcast generation:

```bash
# Start the web interface
python web_app.py

# OR run in the background
nohup python web_app.py > web_app.log 2>&1 &
```

**Web Interface Features:**
- 📁 **File Upload**: Drag & drop or browse to upload JSON files
- 📋 **JSON Paste**: Paste JSON content directly into the web editor
- 📊 **Real-time Status**: Track job progress with live updates
- 📥 **Easy Downloads**: Download generated audio and script files
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices

**Access Points:**
- 🏠 **Main Interface**: http://localhost:5000
- 📊 **Job Status**: http://localhost:5000/status/<job_id>
- 📝 **Example JSON**: http://localhost:5000/example
- 🧹 **Cleanup**: http://localhost:5000/cleanup (admin)

**Usage Steps:**
1. Start the web app: `python web_app.py`
2. Open http://localhost:5000 in your browser
3. Choose to upload a file or paste JSON content
4. Monitor the real-time progress
5. Download your generated podcast when complete

**Web Interface Requirements:**
- All the same requirements as CLI mode
- Flask web framework (automatically installed)
- Modern web browser with JavaScript enabled

### 💻 Command Line Interface

#### Interactive Mode
Run without arguments to use the interactive data source selection:
```bash
python main.py
```
You'll be prompted to choose:
1. 🌐 Online (fetch latest from news source)
2. 📁 Local (use local today.json file)  
3. 🔄 Auto (try online first, fallback to local)

#### Direct File Mode
Directly specify a JSON file for immediate processing:

```bash
# Process a specific JSON file
python main.py -f "data/today.json"

# Process a dated JSON file
python main.py -f "data/04-07-2025/today.json"

# Using full path
python main.py --file "/path/to/your/news-data.json"

# Short form
python main.py -f "path/to/file.json"
```

#### Command Line Options
```bash
python main.py --help
```

**Available options:**
- `-f, --file PATH` - Path to JSON file containing news data
- `-h, --help` - Show help message
- `--version` - Show version information

### Examples
```bash
# Interactive mode (recommended for first time)
python main.py

# Quick generation from existing JSON
python main.py -f "data/04-07-2025/today.json"

# Process custom JSON file
python main.py --file "my-custom-news.json"
```

## 📊 Data Source Options

When running the script, you'll be prompted to choose a data source:

1. **🌐 Online** - Fetch latest from today_arweave.ar.io
2. **📁 Local** - Use local `data/today.json` file
3. **🔄 Auto** - Try online first, fallback to local (recommended)

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

## � Project Structure

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
├── templates/                     # Web interface templates
│   ├── base.html                  # Base template with styling
│   └── index.html                 # Main web interface
├── uploads/                       # Temporary file uploads
├── main.py                        # CLI entry point
├── web_app.py                     # Web interface entry point
├── setup.py                       # Package setup (legacy)
├── pyproject.toml                 # Modern packaging config
├── requirements.txt               # Dependencies
├── .env                           # Environment configuration
├── .env.example                   # Configuration template
└── README.md                      # This file
```

## �🛠️ Advanced Configuration & Troubleshooting

### FFmpeg Configuration
If FFmpeg is not in your system PATH:
1. Download FFmpeg from [official site](https://ffmpeg.org/)
2. Set `FFMPEG_PATH` to the `bin` directory in `.env`

### 🧪 Testing

The main script includes built-in API testing:

```bash
# Run with built-in API testing
python main.py
# The script automatically tests Gemini AI connections

# Test with local data only
python main.py
# Choose option 2 (Local) when prompted
```

### 🐛 Common Issues

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

## 📝 Dependencies & Technical Details

### Core Dependencies
- `google-generativeai` - Gemini AI integration for TTS and transcription
- `yt-dlp==2024.7.16` - Video downloading
- `requests==2.31.0` - HTTP requests
- `python-dotenv==1.0.0` - Environment variable management

### Web Interface Dependencies
- `flask>=3.0.0` - Web framework for the browser interface
- `werkzeug>=3.0.0` - WSGI toolkit for Flask

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

## � Upcoming Features

### 📡 Arweave Permanence Integration
- **Podcast Upload to Arweave**: Automatically upload generated podcasts to the Arweave network for permanent storage
- **Decentralized Distribution**: Serve podcasts directly from the permaweb with permanent, censorship-resistant access
- **Metadata Preservation**: Store podcast metadata, transcripts, and source data permanently on Arweave
- **AR-IO Integration**: Leverage AR-IO gateways for optimized podcast delivery and discovery

### 🐦 Social Media Content Scraping
- **Twitter Thread Scraping**: Automatically extract and process Twitter/X threads related to Arweave ecosystem
- **Real-time Social Monitoring**: Track mentions, discussions, and trending topics across social platforms
- **Community Voice Integration**: Include community discussions and reactions in podcast content
- **Social Sentiment Analysis**: AI-powered analysis of community sentiment and engagement metrics

### 📰 Web Content Extraction
- **Article & Blog Scraping**: Automatically scrape and process articles from Arweave-related websites and blogs
- **URL-based Content Processing**: Direct input of article URLs for immediate processing and inclusion
- **Multi-format Support**: Handle various content formats including Medium, Substack, personal blogs, and news sites
- **Content Summarization**: AI-powered summarization of lengthy articles for podcast-friendly format
- **Source Attribution**: Proper crediting and linking to original sources

### � Enhanced Content Intelligence
- **Cross-platform Aggregation**: Combine content from social media, articles, and official sources
- **Contextual Relevance**: Smart filtering to include only the most relevant and impactful content
- **Automated Research**: AI-driven discovery of related content and background information
- **Dynamic Content Updates**: Real-time integration of breaking news and developments

*These features are actively being developed to create the most comprehensive Arweave ecosystem podcast platform on the permaweb!*

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/tejasmate/arweave-today-ai-podcaster/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tejasmate/arweave-today-ai-podcaster/discussions)
- **Email**: tejasmate@zoho.com

---

Made with ❤️ for the Arweave ecosystem. Building the permanent web, one podcast at a time.
