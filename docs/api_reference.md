# API Reference

## Core Classes

### PodcastGenerator

Main class for orchestrating podcast generation.

```python
from arweave_podcaster import PodcastGenerator

generator = PodcastGenerator("/path/to/project")
success = generator.generate_podcast("auto")
```

#### Methods

- `__init__(base_dir: str)` - Initialize with project base directory
- `generate_podcast(user_choice: str = "auto") -> bool` - Generate complete podcast

### Services

#### GeminiService

Handles Gemini AI integration for script enhancement and TTS.

```python
from arweave_podcaster.services import GeminiService

service = GeminiService(api_key="your_key")
enhanced_script = service.generate_podcast_script(raw_content, date_str)
success = service.generate_audio(script_text, output_path)
```

#### DataService

Manages news data fetching and local storage.

```python
from arweave_podcaster.services import DataService

service = DataService("/path/to/project")
news_data = service.load_news_data_smart("auto")
```

#### VideoService

Handles video downloading and transcription.

```python
from arweave_podcaster.services import VideoService

service = VideoService("/output/directory")
transcript = service.transcribe_video(video_url, "topic_1")
```

## Utility Functions

### Text Processing

```python
from arweave_podcaster.utils.text_utils import (
    clean_script_for_audio,
    format_news_topics,
    create_podcast_opening,
    create_podcast_closing
)

# Clean script for TTS
clean_text = clean_script_for_audio(raw_script)

# Format topics for podcast
formatted = format_news_topics(topics_list)

# Create podcast segments
opening = create_podcast_opening("July 4, 2025")
closing = create_podcast_closing()
```

### File Operations

```python
from arweave_podcaster.utils.file_utils import (
    save_json_file,
    load_json_file,
    save_text_file,
    create_output_filename
)

# File operations
success = save_json_file(data, "/path/to/file.json")
data = load_json_file("/path/to/file.json")
success = save_text_file(content, "/path/to/file.txt")

# Generate standardized filenames
filename = create_output_filename("ArweaveToday", "2025-07-04", "txt")
# Returns: "ArweaveToday-2025-07-04.txt"
```

### Audio Processing

```python
from arweave_podcaster.utils.audio_utils import (
    convert_to_wav,
    parse_audio_mime_type,
    save_binary_file
)

# Audio format conversion
wav_data = convert_to_wav(audio_data, "audio/L16;rate=24000")

# Parse audio parameters
params = parse_audio_mime_type("audio/L16;rate=24000")
# Returns: {"bits_per_sample": 16, "rate": 24000}

# Save audio file
save_binary_file("output.wav", audio_data)
```

### Configuration

```python
from arweave_podcaster.utils.config import config

# Check configuration
if config.is_gemini_configured():
    print("Gemini API ready")

# Validate setup
missing = config.validate_config()
if missing:
    print(f"Missing: {missing}")

# Get paths
output_dir = config.get_output_dir("/base", "04-07-2025")
data_dir = config.get_data_dir("/base", "04-07-2025")
```

## Error Handling

All services and utilities include comprehensive error handling:

- Functions return `None` or `False` on failure
- Errors are logged to console with descriptive messages  
- Graceful degradation when optional services fail
- User-friendly error messages for common issues

## Type Hints

The package includes full type hints for better IDE support:

```python
from typing import Dict, Any, Optional, List

def process_data(data: Dict[str, Any]) -> Optional[str]:
    # Function with proper type annotations
    pass
```
