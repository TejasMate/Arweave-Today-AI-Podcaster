import json
from datetime import datetime
import os
import yt_dlp
from faster_whisper import WhisperModel
import requests
import time
import hashlib
from typing import Dict, Optional
import google.generativeai as genai
import urllib3
from dotenv import load_dotenv
import base64
import mimetypes
import struct
from google import genai as google_genai
from google.genai import types

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Suppress SSL warnings when verification is disabled
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- GEMINI TTS FUNCTIONS ---
def save_binary_file(file_name, data):
    """Save binary audio data to file."""
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"Audio file saved to: {file_name}")

def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
    """Generates a WAV file header for the given audio data and parameters.

    Args:
        audio_data: The raw audio data as a bytes object.
        mime_type: Mime type of the audio data.

    Returns:
        A bytes object representing the WAV file header.
    """
    parameters = parse_audio_mime_type(mime_type)
    bits_per_sample = parameters["bits_per_sample"]
    sample_rate = parameters["rate"]
    num_channels = 1
    data_size = len(audio_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size  # 36 bytes for header fields before data chunk size

    # http://soundfile.sapp.org/doc/WaveFormat/
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",          # ChunkID
        chunk_size,       # ChunkSize (total file size - 8 bytes)
        b"WAVE",          # Format
        b"fmt ",          # Subchunk1ID
        16,               # Subchunk1Size (16 for PCM)
        1,                # AudioFormat (1 for PCM)
        num_channels,     # NumChannels
        sample_rate,      # SampleRate
        byte_rate,        # ByteRate
        block_align,      # BlockAlign
        bits_per_sample,  # BitsPerSample
        b"data",          # Subchunk2ID
        data_size         # Subchunk2Size (size of audio data)
    )
    return header + audio_data

def parse_audio_mime_type(mime_type: str) -> dict[str, int | None]:
    """Parses bits per sample and rate from an audio MIME type string.

    Assumes bits per sample is encoded like "L16" and rate as "rate=xxxxx".

    Args:
        mime_type: The audio MIME type string (e.g., "audio/L16;rate=24000").

    Returns:
        A dictionary with "bits_per_sample" and "rate" keys. Values will be
        integers if found, otherwise None.
    """
    bits_per_sample = 16
    rate = 24000

    # Extract rate from parameters
    parts = mime_type.split(";")
    for param in parts: # Skip the main type part
        param = param.strip()
        if param.lower().startswith("rate="):
            try:
                rate_str = param.split("=", 1)[1]
                rate = int(rate_str)
            except (ValueError, IndexError):
                # Handle cases like "rate=" with no value or non-integer value
                pass # Keep rate as default
        elif param.startswith("audio/L"):
            try:
                bits_per_sample = int(param.split("L", 1)[1])
            except (ValueError, IndexError):
                pass # Keep bits_per_sample as default if conversion fails

    return {"bits_per_sample": bits_per_sample, "rate": rate}

def generate_podcast_audio_with_gemini(script_text: str, output_path: str, api_key: str) -> bool:
    """
    Generate podcast audio using Gemini TTS with Puck voice.
    
    Args:
        script_text: The text script to convert to audio
        output_path: The path to save the output audio file
        api_key: Gemini API key
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print("🎤 Generating podcast audio with Gemini TTS (Puck voice)...")
        
        client = google_genai.Client(api_key=api_key)
        model = "gemini-2.5-flash-preview-tts"
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=script_text),
                ],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            response_modalities=["audio"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Puck"
                    )
                ),
            ),
        )

        audio_chunks = []
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if (
                chunk.candidates is None
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
            ):
                continue
            
            if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                data_buffer = inline_data.data
                
                # Convert to WAV if needed
                if inline_data.mime_type != "audio/wav":
                    data_buffer = convert_to_wav(inline_data.data, inline_data.mime_type)
                
                audio_chunks.append(data_buffer)
        
        if audio_chunks:
            # Combine all audio chunks
            combined_audio = b''.join(audio_chunks)
            
            # Ensure output path has .wav extension for Gemini TTS
            if output_path.endswith('.mp3'):
                output_path = output_path.replace('.mp3', '.wav')
            
            save_binary_file(output_path, combined_audio)
            print(f"✅ Gemini TTS audio generated: {os.path.basename(output_path)}")
            return True
        else:
            print("⚠️ No audio data received from Gemini TTS")
            return False
            
    except Exception as e:
        print(f"⚠️ Error generating audio with Gemini TTS: {e}")
        return False

# --- CONFIGURATION ---
# Configuration is now loaded from .env file
# Copy .env.example to .env and update with your API keys

# FFmpeg configuration
FFMPEG_PATH = os.getenv('FFMPEG_PATH', '')

# Whisper model configuration
WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'tiny.en')

# Data Source Configuration
NEWS_SOURCE_URL = os.getenv('NEWS_SOURCE_URL', 'https://today_arweave.ar.io/')
GITHUB_FALLBACK_URL = os.getenv('GITHUB_FALLBACK_URL', 'https://raw.githubusercontent.com/ArweaveTeam/arweave-today/main/data/today.json')

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
ENABLE_GEMINI_SCRIPT_GENERATION = os.getenv('ENABLE_GEMINI_SCRIPT_GENERATION', 'True').lower() == 'true'


def transcribe_video(video_url: str, output_dir: str, topic_identifier: str = None) -> str:
    """
    Downloads audio from a video URL and transcribes it using Whisper.
    Skips processing if transcript file already exists.

    Args:
        video_url: The URL of the video to transcribe.
        output_dir: The directory to save temporary audio files.
        topic_identifier: Identifier for the topic (e.g., "topic_1", "topic_2")

    Returns:
        The transcribed text, or an empty string if an error occurs.
    """
    try:
        print(f"\nAttempting to transcribe video: {video_url}")
        
        # Generate a clean filename based on topic identifier
        if topic_identifier:
            temp_audio_filename = f"{topic_identifier}_video"
        else:
            # Fallback to timestamp if no identifier provided
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_audio_filename = f"temp_audio_{timestamp}"
        
        # Check if transcript file already exists
        transcript_filename = f"{temp_audio_filename}_transcript.txt"
        transcript_path = os.path.join(output_dir, transcript_filename)
        
        if os.path.exists(transcript_path):
            print(f"📄 Transcript file already exists: {transcript_filename}")
            print("⏭️  Skipping video download and transcription...")
            try:
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read().strip()
                    if existing_content and not existing_content.startswith("[TRANSCRIPTION FAILED"):
                        print("✅ Using existing transcript")
                        return existing_content
                    else:
                        print("⚠️  Existing transcript appears to be empty or failed, re-processing...")
            except Exception as e:
                print(f"⚠️  Could not read existing transcript: {e}, re-processing...")
            
        temp_audio_path_base = os.path.join(output_dir, temp_audio_filename)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': temp_audio_path_base,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': FFMPEG_PATH if FFMPEG_PATH else None,
            'quiet': True,
            'overwrite': True,
        }
        
        # The actual file will have .mp3 extension added by yt-dlp
        temp_audio_path = temp_audio_path_base + '.mp3'

        # Download the audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        print(f"Audio downloaded successfully as {temp_audio_filename}.mp3. Starting transcription...")

        # Transcribe the audio file
        model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        segments, _ = model.transcribe(temp_audio_path, beam_size=5)
        
        transcribed_text = " ".join([segment.text for segment in segments])

        print("Transcription complete.")
        
        # Save the video transcript to a separate file
        try:
            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(transcribed_text.strip())
            print(f"Video transcript saved: {transcript_filename}")
        except Exception as e:
            print(f"Warning: Could not save transcript file: {e}")
        
        # Clean up the temporary audio file
        print(f"Cleaning up temporary file: {temp_audio_filename}.mp3")
        os.remove(temp_audio_path)
        
        return transcribed_text.strip()

    except Exception as e:
        print(f"Could not transcribe video. Error: {e}")
        # Save error info to transcript file if possible
        if 'transcript_path' in locals():
            try:
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    f.write(f"[TRANSCRIPTION FAILED: {e}]")
                print(f"Error logged to: {transcript_filename}")
            except:
                pass
        
        # Clean up if the file exists after an error
        if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
            print(f"Cleaning up temporary file after error: {temp_audio_filename}.mp3")
            os.remove(temp_audio_path)
        return ""


def load_news_data(file_path: str) -> dict:
    """
    Loads the Arweave Today JSON data from a local file.
    
    Args:
        file_path: The path to the JSON file.

    Returns:
        A dictionary containing the news data, or None if an error occurs.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
        return None

def generate_script(news_data: dict, output_dir: str = None) -> str:
    """
    Generates a raw podcast script from the news data, including video transcriptions.
    This will later be processed by Gemini AI for professional script generation.
    
    Args:
        news_data: The news data dictionary
        output_dir: Optional output directory for transcripts. If None, uses default location.
    """
    # Get the publication date
    timestamp_ms = news_data.get('ts', 0)
    pub_date = datetime.fromtimestamp(timestamp_ms / 1000)
    date_str = pub_date.strftime('%B %d, %Y')

    script_lines = [
        f"Welcome to Arweave Today for {date_str}.",
        "Here are the latest updates from across the permaweb ecosystem.",
        "--------------------",
        "MAIN STORIES:"
    ]
    
    # Use provided output_dir or default to generic output folder
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output')

    for i, topic in enumerate(news_data.get('topics', []), 1):
        # Add clear topic separation marker
        script_lines.append(f"=== TOPIC {i} START ===")
        
        headline = topic.get('headline', 'No headline')
        body = topic.get('body', 'No content.')
        nature = topic.get('nature', 'news')
        
        script_lines.append(f"In {nature} news: {headline}.")
        script_lines.append(body)

        # --- Check for and transcribe video with topic identifier ---
        if 'video' in topic and topic['video']:
            video_url = topic['video']
            topic_identifier = f"topic_{i}"
            transcript = transcribe_video(video_url, output_dir, topic_identifier)
            if transcript:
                script_lines.append("\n[Video Transcript]:")
                script_lines.append(transcript)
        
        # Add clear topic separation marker
        script_lines.append(f"=== TOPIC {i} END ===")
        script_lines.append("") # Add a blank line for separation

    # --- Chit-Chat Segment ---
    chitchat = news_data.get('chitchat')
    if chitchat:
        script_lines.append("=== CHITCHAT SECTION START ===")
        script_lines.append("-" * 20)
        script_lines.append("DID YOU KNOW?:")
        headline = chitchat.get('headline', 'No headline')
        body = chitchat.get('body', 'No content').replace('\n\n', ' ')
        script_lines.append(f"{headline}: {body}")
        script_lines.append("=== CHITCHAT SECTION END ===")
        script_lines.append("")

    # --- Suggested Read ---
    suggested = news_data.get('suggested')
    if suggested:
        script_lines.append("=== SUGGESTED READ SECTION START ===")
        script_lines.append("-" * 20)
        script_lines.append("TODAY'S SUGGESTED READ:")
        headline = suggested.get('headline', 'No headline')
        body = suggested.get('body', 'No content').replace('\n\n', ' ')
        script_lines.append(f"'{headline}'.")
        script_lines.append(body)
        script_lines.append("=== SUGGESTED READ SECTION END ===")
        script_lines.append("")

    # --- Outro ---
    script_lines.append("-" * 20)
    script_lines.append("That's all for Arweave Today. Thanks for listening.")
    
    return "\n".join(script_lines)

def save_script_to_file(script_text: str, output_path: str):
    """
    Saves the text script to a file.

    Args:
        script_text: The text script to save.
        output_path: The path to save the output TXT file.
    """
    try:
        print(f"Saving transcript to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script_text)
        print("Transcript file saved successfully.")
    except Exception as e:
        print(f"An error occurred while saving the transcript: {e}")

def save_script_to_audio(script_text: str, output_path: str):
    """
    Converts a text script to an audio file using Gemini TTS.

    Args:
        script_text: The text script to convert.
        output_path: The path to save the output MP3/WAV file.
    """
    try:
        # Clean the script text for audio generation
        cleaned_text = clean_script_for_audio(script_text)
        
        print(f"Converting script to audio at: {output_path}")
        
        # Try Gemini TTS first if API key is available
        audio_generated = False
        if GEMINI_API_KEY and GEMINI_API_KEY.strip():
            audio_generated = generate_podcast_audio_with_gemini(cleaned_text, output_path, GEMINI_API_KEY)
        
        if not audio_generated:
            print("⚠️ Gemini TTS failed or not available. Please configure GEMINI_API_KEY in .env file.")
            return
        
        print("Audio file saved successfully.")
        
    except Exception as e:
        print(f"An error occurred during text-to-speech conversion: {e}")

def save_script_to_audio_with_gemini(script_text: str, output_path: str, gemini_processor = None):
    """
    Converts a text script to an audio file using Gemini TTS.

    Args:
        script_text: The text script to convert.
        output_path: The path to save the output MP3/WAV file.
        gemini_processor: GeminiScriptProcessor instance for enhanced TTS
    """
    try:
        audio_generated = False
        
        # Try Gemini TTS directly
        if GEMINI_API_KEY and GEMINI_API_KEY.strip():
            # Clean the script text for audio generation
            cleaned_text = clean_script_for_audio(script_text)
            audio_generated = generate_podcast_audio_with_gemini(cleaned_text, output_path, GEMINI_API_KEY)
        
        # Fallback message if Gemini TTS fails
        if not audio_generated:
            print("⚠️ Gemini TTS failed or not available. Please configure GEMINI_API_KEY in .env file.")
            return
        
    except Exception as e:
        print(f"An error occurred during text-to-speech conversion: {e}")

class GeminiScriptProcessor:
    """
    Handles Gemini AI script generation and text-to-speech for professional podcast creation.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the Gemini script processor.
        
        Args:
            api_key: Your Gemini API key
        """
        self.api_key = api_key
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
            self.model = None
    
    def generate_podcast_script(self, raw_content: str, date_str: str) -> str:
        """
        Generate a professional podcast script from raw content using Gemini AI.
        
        Args:
            raw_content: The raw combined content from news and video transcripts
            date_str: The formatted date string for the podcast
            
        Returns:
            Professional podcast script or original content if generation fails
        """
        if not self.model:
            print("Gemini model not available, using raw content")
            return raw_content
        
        try:
            print("🤖 Generating professional podcast script with Gemini AI...")
            
            prompt = f"""
You are a professional podcast script writer for "Arweave Today," a daily news podcast about the Arweave ecosystem and decentralized web technologies.

Transform the following raw content into a polished, engaging podcast script for {date_str}:

GUIDELINES:
1. Create a natural, conversational flow suitable for audio
2. Use clear transitions between topics
3. Explain technical terms in accessible language
4. Maintain an enthusiastic but professional tone
5. Keep the existing structure: Welcome → Main Stories → Did You Know → Suggested Read → Outro
6. When video transcripts are included, summarize key points naturally rather than reading verbatim
7. Make it sound like a human host is speaking, not reading a script
8. Include natural pauses and emphasis cues with punctuation
9. Keep segments concise and engaging
10. Maintain the technical accuracy while improving readability
11. AVOID stage directions, music cues, or formatting elements that shouldn't be read aloud
12. Don't include text like "(Intro Music)", "**(Host:**", "---", or similar formatting
13. Focus on spoken content only - what the host would actually say

RAW CONTENT:
{raw_content}

Generate a professional podcast script that flows naturally when spoken aloud. Focus on making it sound conversational and engaging for listeners interested in Arweave and decentralized technologies. Output only the spoken content without any stage directions or formatting elements.
"""

            response = self.model.generate_content(prompt)
            
            if response and response.text:
                print("✅ Professional script generated successfully!")
                return response.text.strip()
            else:
                print("⚠️ Empty response from Gemini, using raw content")
                return raw_content
                
        except Exception as e:
            print(f"⚠️ Error generating script with Gemini: {e}")
            print("Using raw content as fallback")
            return raw_content
    
    def generate_audio_with_gemini(self, script_text: str, output_path: str) -> bool:
        """
        Generate audio from text using Gemini AI's text-to-speech capabilities with natural Puck voice.
        
        Args:
            script_text: The text script to convert to audio
            output_path: The path to save the output audio file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print("🎤 Generating podcast audio with Gemini AI (Puck voice)...")
            
            # Clean the script text for audio generation first
            cleaned_text = clean_script_for_audio(script_text)
            
            # Prepare the text for natural, conversational TTS with Puck personality
            enhanced_prompt = f"""
Transform this podcast script to sound natural and conversational like "Puck" - a friendly, enthusiastic but not overly excited tech podcaster. Make it sound human and engaging:

VOICE CHARACTERISTICS FOR "PUCK":
- Conversational and warm tone
- Natural speech patterns with varied sentence lengths
- Friendly but professional delivery
- Enthusiastic about technology without being robotic
- Uses natural filler words occasionally (like "you know", "so", "well")
- Speaks like explaining to a friend, not reading from a script

OPTIMIZATION FOR TTS:
1. Add natural speech pauses with commas, periods, and ellipses
2. Break up long technical sentences into digestible chunks
3. Add pronunciation cues for technical terms (AR-weave, not Arweave)
4. Include natural emphasis with capitalization or punctuation
5. Make transitions sound conversational and smooth
6. Add breathing room between sections
7. Remove any remaining stage directions, formatting marks, or non-speech elements

Original script:
{cleaned_text}

Return the Puck-optimized, natural-sounding version ready for text-to-speech:
"""
            
            response = self.model.generate_content(enhanced_prompt)
            
            if response and response.text:
                optimized_text = response.text.strip()
                print("✅ Script optimized for natural Puck voice")
                
                # Use Gemini TTS with the optimized text
                print("🎵 Converting to natural audio with Gemini TTS...")
                return generate_podcast_audio_with_gemini(optimized_text, output_path, self.api_key)
            else:
                print("⚠️ Failed to optimize script for Puck voice, using original text with Gemini TTS")
                return generate_podcast_audio_with_gemini(cleaned_text, output_path, self.api_key)
                
        except Exception as e:
            print(f"⚠️ Error generating audio with Gemini: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test if Gemini API connection is working.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.model:
            return False
            
        try:
            test_response = self.model.generate_content("Hello, this is a test.")
            return bool(test_response and test_response.text)
        except Exception as e:
            print(f"Gemini connection test failed: {e}")
            return False

def test_integrations():
    """
    Test function to verify all API integrations are working.
    """
    print("Testing API integrations...")
    
    # Test Gemini
    gemini_available = False
    if GEMINI_API_KEY and GEMINI_API_KEY.strip():
        try:
            gemini_processor = GeminiScriptProcessor(GEMINI_API_KEY)
            if gemini_processor.test_connection():
                print("✅ Gemini AI connection successful")
                gemini_available = True
            else:
                print("❌ Gemini AI connection failed")
        except Exception as e:
            print(f"❌ Gemini AI initialization failed: {e}")
    else:
        print("⚠️ Gemini API key not configured")
    
    return gemini_available

def fetch_online_news_data(url: str = None) -> dict:
    """
    Fetches the latest Arweave Today JSON data from the online source.
    
    Args:
        url: The URL to fetch the JSON data from. If None, uses NEWS_SOURCE_URL from env.

    Returns:
        A dictionary containing the news data, or None if an error occurs.
    """
    if url is None:
        url = NEWS_SOURCE_URL
        
    try:
        print(f"🌐 Fetching latest news data from: {url}")
        
        # Try with SSL verification first
        try:
            response = requests.get(url, timeout=30, verify=True)
            response.raise_for_status()
        except requests.exceptions.SSLError:
            print("⚠️ SSL verification failed, retrying without SSL verification...")
            # Fallback without SSL verification
            response = requests.get(url, timeout=30, verify=False)
            response.raise_for_status()
        
        # Check if response is JSON
        content_type = response.headers.get('content-type', '').lower()
        if 'application/json' in content_type or url.endswith('.json'):
            # Direct JSON response
            news_data = response.json()
        else:
            # Might be HTML page, try to find JSON data or redirect
            print("🔍 Response is not JSON, checking for data...")
            
            # Try common JSON endpoint variations
            json_urls = [
                url.rstrip('/') + '/data.json',
                url.rstrip('/') + '/today.json',
                url.rstrip('/') + '/api/today',
                GITHUB_FALLBACK_URL
            ]
            
            news_data = None
            for json_url in json_urls:
                try:
                    print(f"🔄 Trying: {json_url}")
                    json_response = requests.get(json_url, timeout=30, verify=False)
                    if json_response.status_code == 200:
                        news_data = json_response.json()
                        print(f"✅ Found JSON data at: {json_url}")
                        break
                except:
                    continue
            
            if not news_data:
                print("❌ Could not find JSON data at any endpoint")
                return None
        
        print("✅ Online news data fetched successfully!")
        return news_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error fetching online data: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON from online source: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error fetching online data: {e}")
        return None

def save_news_data_locally(news_data: dict) -> bool:
    """
    Saves the fetched news data to a date-based directory structure.
    
    Args:
        news_data: The news data dictionary to save.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        # Create date-based directory structure from JSON timestamp
        if 'ts' in news_data:
            timestamp_ms = news_data.get('ts', 0)
            pub_date = datetime.fromtimestamp(timestamp_ms / 1000)
            date_folder = pub_date.strftime('%d-%m-%Y')
            
            # Create date-based directory in data folder
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(script_dir)  # Go up to project root
            date_dir = os.path.join(base_dir, 'data', date_folder)
            os.makedirs(date_dir, exist_ok=True)
            
            # Save in the date-based directory
            date_file_path = os.path.join(date_dir, 'today.json')
            with open(date_file_path, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, indent=2, ensure_ascii=False)
            print(f"📅 News data saved in date directory: {date_folder}/today.json")
            return True
        else:
            print("⚠️ No timestamp found in news data, cannot create date-based directory")
            return False
            
    except Exception as e:
        print(f"⚠️ Could not save news data locally: {e}")
        return False

def get_user_choice_for_data_source() -> str:
    """
    Prompts the user to choose between online or local data source.
    
    Returns:
        'online' or 'local' based on user choice.
    """
    print("\n" + "="*50)
    print("📊 DATA SOURCE SELECTION")
    print("="*50)
    print("Choose your data source:")
    print("1. 🌐 Online (fetch latest from news source)")
    print("2. 📁 Local (use local today.json file)")
    print("3. 🔄 Auto (try online first, fallback to local)")
    
    while True:
        try:
            choice = input("\nEnter your choice (1/2/3) or press Enter for Auto: ").strip()
            
            if choice == "" or choice == "3":
                return "auto"
            elif choice == "1":
                return "online"
            elif choice == "2":
                return "local"
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or press Enter.")
        except KeyboardInterrupt:
            print("\n🛑 Operation cancelled by user.")
            return "local"  # Default fallback

def load_news_data_smart(script_dir: str, user_choice: str = "auto") -> dict:
    """
    Intelligently loads news data based on user preference.
    
    Args:
        script_dir: Directory where the script is located.
        user_choice: 'online', 'local', or 'auto'.
        
    Returns:
        A dictionary containing the news data, or None if all sources fail.
    """
    local_file_path = os.path.join(script_dir, '..', 'data', 'today.json')
    
    if user_choice == "online":
        # User specifically wants online data
        print("🌐 Fetching online data as requested...")
        news_data = fetch_online_news_data()
        if news_data:
            # Save to date-based directory
            save_news_data_locally(news_data)
            return news_data
        else:
            print("❌ Failed to fetch online data.")
            print("💡 Would you like to try local data instead? (y/n)")
            try:
                fallback_choice = input().strip().lower()
                if fallback_choice in ['y', 'yes', '']:
                    print("🔄 Falling back to local data...")
                    local_data = load_news_data(local_file_path)
                    if local_data:
                        print("✅ Using local data file.")
                        return local_data
                    else:
                        print("⚠️ Local file also failed, trying most recent date directory...")
                        recent_file = get_most_recent_date_directory(script_dir)
                        if recent_file:
                            recent_data = load_news_data(recent_file)
                            if recent_data:
                                print("✅ Using most recent date directory data.")
                                return recent_data
            except KeyboardInterrupt:
                print("\n🛑 Operation cancelled.")
            return None
            
    elif user_choice == "local":
        # User specifically wants local data
        print("📁 Using local data as requested...")
        local_data = load_news_data(local_file_path)
        if local_data:
            return local_data
        else:
            # Try most recent date directory as fallback
            print("⚠️ Standard local file not found, trying most recent date directory...")
            recent_file = get_most_recent_date_directory(script_dir)
            if recent_file:
                recent_data = load_news_data(recent_file)
                if recent_data:
                    print("✅ Using most recent date directory data.")
                    return recent_data
            return None
        
    else:  # user_choice == "auto"
        # Try online first, fallback to local
        print("🔄 Auto mode: Trying online first...")
        news_data = fetch_online_news_data()
        
        if news_data:
            # Online successful - save to date directory and use it
            save_news_data_locally(news_data)
            return news_data
        else:
            # Online failed - try local file
            print("⚠️ Online fetch failed, trying local file...")
            local_data = load_news_data(local_file_path)
            
            if local_data:
                print("✅ Using local data file.")
                return local_data
            else:
                # Local also failed - try most recent date directory
                print("⚠️ Local file failed, trying most recent date directory...")
                recent_file = get_most_recent_date_directory(script_dir)
                
                if recent_file:
                    recent_data = load_news_data(recent_file)
                    if recent_data:
                        print("✅ Using most recent date directory data.")
                        return recent_data
                else:
                    print("❌ All data sources failed.")
                    return None

def get_most_recent_date_directory(script_dir: str) -> str:
    """
    Finds the most recent date directory in the data folder.
    
    Args:
        script_dir: Directory where the script is located.
        
    Returns:
        Path to the most recent today.json file, or None if not found.
    """
    try:
        data_dir = os.path.join(script_dir, '..', 'data')
        if not os.path.exists(data_dir):
            return None
            
        # Get all directories that match the date format
        date_dirs = []
        for item in os.listdir(data_dir):
            item_path = os.path.join(data_dir, item)
            if os.path.isdir(item_path):
                # Check if it matches DD-MM-YYYY format
                try:
                    datetime.strptime(item, '%d-%m-%Y')
                    today_json_path = os.path.join(item_path, 'today.json')
                    if os.path.exists(today_json_path):
                        date_dirs.append((item, today_json_path))
                except ValueError:
                    continue
        
        if not date_dirs:
            return None
            
        # Sort by date (newest first)
        date_dirs.sort(key=lambda x: datetime.strptime(x[0], '%d-%m-%Y'), reverse=True)
        most_recent = date_dirs[0][1]
        print(f"📅 Found most recent data: {date_dirs[0][0]}/today.json")
        return most_recent
        
    except Exception as e:
        print(f"⚠️ Error finding recent date directory: {e}")
        return None

def clean_script_for_audio(script_text: str) -> str:
    """
    Cleans the script text for audio generation by removing stage directions, 
    formatting elements, and other text that shouldn't be read aloud.
    
    Args:
        script_text: The raw script text with formatting elements
        
    Returns:
        Cleaned text suitable for text-to-speech conversion
    """
    import re
    
    # Remove lines with stage directions in double asterisks
    script_text = re.sub(r'\*\*.*?\*\*', '', script_text)
    
    # Remove separator lines with dashes
    script_text = re.sub(r'^-{3,}.*$', '', script_text, flags=re.MULTILINE)
    script_text = re.sub(r'^={3,}.*$', '', script_text, flags=re.MULTILINE)
    
    # Remove transition sound effect markers
    script_text = re.sub(r'\(.*?sound effect.*?\)', '', script_text, flags=re.IGNORECASE)
    script_text = re.sub(r'\(.*?transition.*?\)', '', script_text, flags=re.IGNORECASE)
    script_text = re.sub(r'\(.*?music.*?\)', '', script_text, flags=re.IGNORECASE)
    
    # Remove other parenthetical stage directions
    script_text = re.sub(r'\(.*?fades? in.*?\)', '', script_text, flags=re.IGNORECASE)
    script_text = re.sub(r'\(.*?fades? out.*?\)', '', script_text, flags=re.IGNORECASE)
    script_text = re.sub(r'\(.*?fades? up.*?\)', '', script_text, flags=re.IGNORECASE)
    script_text = re.sub(r'\(.*?plays to end.*?\)', '', script_text, flags=re.IGNORECASE)
    
    # Remove host labels and formatting
    script_text = re.sub(r'^\*\*Host:\*\*\s*', '', script_text, flags=re.MULTILINE)
    script_text = re.sub(r'^Host:\s*', '', script_text, flags=re.MULTILINE)
    
    # Clean up multiple newlines and whitespace
    script_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', script_text)
    script_text = re.sub(r'^\s+', '', script_text, flags=re.MULTILINE)
    script_text = re.sub(r'\s+$', '', script_text, flags=re.MULTILINE)
    
    # Remove empty lines at start and end
    script_text = script_text.strip()
    
    return script_text

def main():
    """
    Main function to drive the podcast script generation with video transcription and AI enhancement.
    """
    print("🎙️  ARWEAVE TODAY SCRIPT GENERATOR")
    print("="*50)
    
    # Test API integrations
    gemini_available = test_integrations()
    
    if gemini_available:
        print("🤖 AI script enhancement will be enabled")
    else:
        print("⚠️  AI script enhancement will be disabled - using raw script")
    
    print("="*50)
    
    # Build the path to the data file relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get user's preference for data source
    user_choice = get_user_choice_for_data_source()
    
    # Load news data using smart loading (online/local/auto)
    news_data = load_news_data_smart(script_dir, user_choice)
    if not news_data:
        print("❌ Could not load news data from any source. Exiting.")
        return

    # Create the output directory structure based on date
    timestamp_ms = news_data.get('ts', 0)
    pub_date = datetime.fromtimestamp(timestamp_ms / 1000)
    date_folder = pub_date.strftime('%d-%m-%Y')
    
    # Create date-based output directory
    base_output_dir = os.path.join(script_dir, '..', 'output')
    output_dir = os.path.join(base_output_dir, date_folder)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📁 Output directory: output/{date_folder}")

    # Generate the raw podcast script (including video transcription)
    print("📝 Generating raw podcast script with video transcription...")
    raw_script_content = generate_script(news_data, output_dir)

    # Get the publication date for Gemini processing
    timestamp_ms = news_data.get('ts', 0)
    pub_date = datetime.fromtimestamp(timestamp_ms / 1000)
    date_str = pub_date.strftime('%B %d, %Y')

    # Process with Gemini AI if available
    gemini_processor = None
    if gemini_available and ENABLE_GEMINI_SCRIPT_GENERATION:
        print("🤖 Enhancing script with Gemini AI...")
        gemini_processor = GeminiScriptProcessor(GEMINI_API_KEY)
        final_script_content = gemini_processor.generate_podcast_script(raw_script_content, date_str)
    else:
        print("📄 Using raw script (Gemini AI not available or disabled)")
        final_script_content = raw_script_content

    # Define output file paths
    datestamp = datetime.fromtimestamp(news_data['ts'] / 1000).strftime('%Y-%m-%d')
    base_filename = f"ArweaveToday-{datestamp}"
    
    # Save both raw and final scripts
    raw_transcript_path = os.path.join(output_dir, f"{base_filename}-raw.txt")
    final_transcript_path = os.path.join(output_dir, f"{base_filename}.txt")
    final_audio_path = os.path.join(output_dir, f"{base_filename}.mp3")

    # Save the raw script
    print("💾 Saving raw transcript...")
    save_script_to_file(raw_script_content, raw_transcript_path)
    
    # Save the final script
    print("💾 Saving final enhanced transcript...")
    save_script_to_file(final_script_content, final_transcript_path)
    
    # Generate audio using Gemini-enhanced TTS
    print("🎤 Converting final script to podcast audio...")
    save_script_to_audio_with_gemini(final_script_content, final_audio_path, gemini_processor)
    
    print("\n" + "="*50)
    print("✅ PODCAST GENERATION COMPLETE!")
    print("="*50)
    print(f"📄 Raw Script: {os.path.basename(raw_transcript_path)}")
    print(f"🎯 Final Script: {os.path.basename(final_transcript_path)}")
    print(f"🎵 Audio File: {os.path.basename(final_audio_path)}")
    print(f"📁 Location: {output_dir}")
    if gemini_available:
        print("🤖 Enhanced with Gemini AI (Script + Audio)")
    print("="*50)

if __name__ == "__main__":
    main()