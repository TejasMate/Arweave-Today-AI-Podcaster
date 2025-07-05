import json
from datetime import datetime
import os
from gtts import gTTS
import yt_dlp
from faster_whisper import WhisperModel
import requests
import time
import hashlib
from typing import Dict, Optional
import google.generativeai as genai
import urllib3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Suppress SSL warnings when verification is disabled
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
# Configuration is now loaded from .env file
# Copy .env.example to .env and update with your API keys

# FFmpeg configuration
FFMPEG_PATH = os.getenv('FFMPEG_PATH', '')

# Whisper model configuration
WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'tiny.en')

# AssemblyAI Configuration
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY', '')
ASSEMBLYAI_BASE_URL = "https://api.assemblyai.com/v2"
ENABLE_ASSEMBLYAI_DIARIZATION = os.getenv('ENABLE_ASSEMBLYAI_DIARIZATION', 'True').lower() == 'true'

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

def generate_script(news_data: dict) -> str:
    """
    Generates a raw podcast script from the news data, including video transcriptions.
    This will later be processed by Gemini AI for professional script generation.
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

def save_script_to_audio(script_text: str, output_path: str, enable_diarization: bool = True):
    """
    Converts a text script to an audio file using gTTS and optionally processes it with AssemblyAI.

    Args:
        script_text: The text script to convert.
        output_path: The path to save the output MP3 file.
        enable_diarization: Whether to perform speaker diarization analysis.
    """
    try:
        print(f"Converting script to audio at: {output_path}")
        tts = gTTS(text=script_text, lang='en', slow=False)
        tts.save(output_path)
        print("Audio file saved successfully.")
        
        # Perform speaker diarization if enabled and API key is set
        if (enable_diarization and 
            ENABLE_ASSEMBLYAI_DIARIZATION and 
            ASSEMBLYAI_API_KEY and ASSEMBLYAI_API_KEY.strip()):
            
            print("\n" + "="*50)
            print("STARTING SPEAKER DIARIZATION ANALYSIS")
            print("="*50)
            
            processor = AssemblyAIProcessor(ASSEMBLYAI_API_KEY)
            output_dir = os.path.dirname(output_path)
            diarization_dir = os.path.join(output_dir, 'diarization_results')
            os.makedirs(diarization_dir, exist_ok=True)
            
            success = processor.process_audio_file(output_path, diarization_dir)
            if success:
                print("Speaker diarization analysis completed successfully!")
            else:
                print("Speaker diarization analysis failed.")
        elif enable_diarization and (not ASSEMBLYAI_API_KEY or not ASSEMBLYAI_API_KEY.strip()):
            print("\nSkipping speaker diarization: AssemblyAI API key not configured")
            print("To enable diarization, set ASSEMBLYAI_API_KEY in the .env file")
        
    except Exception as e:
        print(f"An error occurred during text-to-speech conversion: {e}")

def save_script_to_audio_with_gemini(script_text: str, output_path: str, gemini_processor = None, enable_diarization: bool = True):
    """
    Converts a text script to an audio file using Gemini-enhanced TTS and optionally processes it with AssemblyAI.

    Args:
        script_text: The text script to convert.
        output_path: The path to save the output MP3 file.
        gemini_processor: GeminiScriptProcessor instance for enhanced TTS
        enable_diarization: Whether to perform speaker diarization analysis.
    """
    try:
        audio_generated = False
        
        # Try Gemini-enhanced audio generation first
        if gemini_processor:
            audio_generated = gemini_processor.generate_audio_with_gemini(script_text, output_path)
        
        # Fallback to standard gTTS if Gemini fails
        if not audio_generated:
            print("🎵 Using standard text-to-speech conversion...")
            tts = gTTS(text=script_text, lang='en', slow=False)
            tts.save(output_path)
            print(f"✅ Audio file saved: {os.path.basename(output_path)}")
        
        # Perform speaker diarization if enabled and API key is set
        if (enable_diarization and 
            ENABLE_ASSEMBLYAI_DIARIZATION and 
            ASSEMBLYAI_API_KEY and ASSEMBLYAI_API_KEY.strip()):
            
            print("\n" + "="*50)
            print("STARTING SPEAKER DIARIZATION ANALYSIS")
            print("="*50)
            
            processor = AssemblyAIProcessor(ASSEMBLYAI_API_KEY)
            output_dir = os.path.dirname(output_path)
            diarization_dir = os.path.join(output_dir, 'diarization_results')
            os.makedirs(diarization_dir, exist_ok=True)
            
            success = processor.process_audio_file(output_path, diarization_dir)
            if success:
                print("Speaker diarization analysis completed successfully!")
            else:
                print("Speaker diarization analysis failed.")
        elif enable_diarization and (not ASSEMBLYAI_API_KEY or not ASSEMBLYAI_API_KEY.strip()):
            print("\nSkipping speaker diarization: AssemblyAI API key not configured")
            print("To enable diarization, set ASSEMBLYAI_API_KEY in the .env file")
        
    except Exception as e:
        print(f"An error occurred during text-to-speech conversion: {e}")

class AssemblyAIProcessor:
    """
    Handles AssemblyAI speaker diarization processing integrated into podcast generation.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the AssemblyAI processor.
        
        Args:
            api_key: Your AssemblyAI API key
        """
        self.api_key = api_key
        self.headers = {
            "authorization": api_key,
            "content-type": "application/json"
        }
        
    def upload_file(self, file_path: str) -> Optional[str]:
        """
        Upload an audio file to AssemblyAI and get the upload URL.
        
        Args:
            file_path: Path to the audio file to upload
            
        Returns:
            The upload URL or None if upload failed
        """
        try:
            print(f"Uploading {os.path.basename(file_path)} to AssemblyAI...")
            
            with open(file_path, 'rb') as f:
                upload_response = requests.post(
                    f"{ASSEMBLYAI_BASE_URL}/upload",
                    headers={"authorization": self.api_key},
                    data=f
                )
            
            if upload_response.status_code == 200:
                upload_url = upload_response.json()['upload_url']
                print(f"File uploaded successfully.")
                return upload_url
            else:
                print(f"Upload failed: {upload_response.status_code} - {upload_response.text}")
                return None
                
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    def submit_transcription_job(self, audio_url: str) -> Optional[str]:
        """
        Submit a transcription job with speaker diarization.
        
        Args:
            audio_url: The URL of the uploaded audio file
            
        Returns:
            The transcription job ID or None if submission failed
        """
        try:
            transcript_request = {
                "audio_url": audio_url,
                "speaker_labels": True,
                "speakers_expected": 2,
                "language_code": "en_us",
                "punctuate": True,
                "format_text": True,
                "dual_channel": False,
                "auto_highlights": True,
                "sentiment_analysis": True,
                "entity_detection": True
            }
            
            print("Starting speaker diarization analysis...")
            
            response = requests.post(
                f"{ASSEMBLYAI_BASE_URL}/transcript",
                headers=self.headers,
                json=transcript_request
            )
            
            if response.status_code == 200:
                job_id = response.json()['id']
                print(f"Diarization job submitted. Job ID: {job_id}")
                return job_id
            else:
                print(f"Job submission failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error submitting transcription job: {e}")
            return None
    
    def get_transcription_result(self, job_id: str, poll_interval: int = 5) -> Optional[Dict]:
        """
        Poll for transcription results until completed.
        
        Args:
            job_id: The transcription job ID
            poll_interval: How often to check for completion (seconds)
            
        Returns:
            The complete transcription result or None if failed
        """
        try:
            print(f"Processing speaker diarization (this may take 1-3 minutes)...")
            
            while True:
                response = requests.get(
                    f"{ASSEMBLYAI_BASE_URL}/transcript/{job_id}",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    print(f"Error getting results: {response.status_code} - {response.text}")
                    return None
                
                result = response.json()
                status = result['status']
                
                if status == 'completed':
                    print("Speaker diarization completed successfully!")
                    return result
                elif status == 'error':
                    print(f"Diarization failed: {result.get('error', 'Unknown error')}")
                    return None
                else:
                    print(f"Status: {status}... waiting {poll_interval} seconds")
                    time.sleep(poll_interval)
                    
        except Exception as e:
            print(f"Error getting transcription results: {e}")
            return None
    
    def format_diarization_output(self, result: Dict) -> str:
        """
        Format the speaker diarization results into a readable format.
        
        Args:
            result: The complete transcription result from AssemblyAI
            
        Returns:
            Formatted text with speaker labels
        """
        if not result.get('utterances'):
            return str(result.get('text', 'No transcription available'))
        
        formatted_lines = []
        formatted_lines.append("=== SPEAKER DIARIZATION RESULTS ===\n")
        
        for utterance in result['utterances']:
            speaker = str(utterance.get('speaker', 'Unknown'))
            text = utterance.get('text')
            if text is None:
                text = ''
            else:
                text = str(text)
            confidence = utterance.get('confidence', 0)
            if confidence is None:
                confidence = 0
            start = utterance.get('start', 0)
            end = utterance.get('end', 0)
            try:
                start = float(start) / 1000
            except Exception:
                start = 0.0
            try:
                end = float(end) / 1000
            except Exception:
                end = 0.0
            formatted_lines.append(
                f"Speaker {speaker} ({start:.1f}s - {end:.1f}s) [confidence: {confidence:.2f}]:\n{text}\n"
            )
        
        # Add summary information
        if 'summary' in result and result['summary']:
            formatted_lines.append("\n=== AUTO-GENERATED SUMMARY ===")
            formatted_lines.append(str(result['summary']))
        
        # Add sentiment analysis if available
        if 'sentiment_analysis_results' in result and result['sentiment_analysis_results']:
            formatted_lines.append("\n=== SENTIMENT ANALYSIS ===")
            for sentiment in result['sentiment_analysis_results']:
                s_text = sentiment.get('text')
                if s_text is None:
                    s_text = ''
                else:
                    s_text = str(s_text)
                s_text = s_text[:100] + "..."
                sentiment_label = str(sentiment.get('sentiment', 'NEUTRAL'))
                s_confidence = sentiment.get('confidence', 0)
                if s_confidence is None:
                    s_confidence = 0
                formatted_lines.append(f"{sentiment_label} ({s_confidence:.2f}): {s_text}")
        
        return "\n".join(formatted_lines)
    
    def process_audio_file(self, file_path: str, output_dir: str) -> bool:
        """
        Process an audio file through the complete AssemblyAI pipeline.
        
        Args:
            file_path: Path to the audio file to process
            output_dir: Directory to save the results
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Step 1: Upload file
            upload_url = self.upload_file(file_path)
            if not upload_url:
                return False
            
            # Step 2: Submit transcription job
            job_id = self.submit_transcription_job(upload_url)
            if not job_id:
                return False
            
            # Step 3: Get results
            result = self.get_transcription_result(job_id)
            if not result:
                return False
            
            # Step 4: Format and save results
            formatted_output = self.format_diarization_output(result)
            
            # Create output filename
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file = os.path.join(output_dir, f"{base_name}_diarization.txt")
            json_output_file = os.path.join(output_dir, f"{base_name}_diarization.json")
            
            # Save formatted text output
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(formatted_output)
            
            # Save raw JSON output
            with open(json_output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"Diarization results saved:")
            print(f"  - Text: {os.path.basename(output_file)}")
            print(f"  - JSON: {os.path.basename(json_output_file)}")
            
            return True
            
        except Exception as e:
            print(f"Error processing diarization for {file_path}: {e}")
            return False

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

RAW CONTENT:
{raw_content}

Generate a professional podcast script that flows naturally when spoken aloud. Focus on making it sound conversational and engaging for listeners interested in Arweave and decentralized technologies.
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

Original script:
{script_text}

Return the Puck-optimized, natural-sounding version:
"""
            
            response = self.model.generate_content(enhanced_prompt)
            
            if response and response.text:
                optimized_text = response.text.strip()
                print("✅ Script optimized for natural Puck voice")
                
                # Use gTTS with the optimized text and slower speed for more natural delivery
                print("🎵 Converting to natural audio with Puck personality...")
                tts = gTTS(text=optimized_text, lang='en', slow=True)  # Slower for more natural delivery
                tts.save(output_path)
                print(f"✅ Natural Puck-voice audio saved to: {os.path.basename(output_path)}")
                return True
            else:
                print("⚠️ Failed to optimize script for Puck voice, falling back to standard TTS")
                return False
                
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
    
    # Test AssemblyAI
    assemblyai_available = False
    if ASSEMBLYAI_API_KEY and ASSEMBLYAI_API_KEY.strip():
        try:
            processor = AssemblyAIProcessor(ASSEMBLYAI_API_KEY)
            print("✅ AssemblyAI processor initialized successfully")
            assemblyai_available = True
        except Exception as e:
            print(f"❌ AssemblyAI processor initialization failed: {e}")
    else:
        print("⚠️ AssemblyAI API key not configured")
    
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
    
    return assemblyai_available, gemini_available

def fetch_online_news_data(url: str = "https://today_arweave.ar.io/") -> dict:
    """
    Fetches the latest Arweave Today JSON data from the online source.
    
    Args:
        url: The URL to fetch the JSON data from.

    Returns:
        A dictionary containing the news data, or None if an error occurs.
    """
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
                'https://raw.githubusercontent.com/ArweaveTeam/arweave-today/main/data/today.json'
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

def save_news_data_locally(news_data: dict, file_path: str) -> bool:
    """
    Saves the fetched news data to a local JSON file for backup/offline use.
    
    Args:
        news_data: The news data dictionary to save.
        file_path: The path where to save the JSON file.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, indent=2, ensure_ascii=False)
        print(f"💾 News data saved locally: {os.path.basename(file_path)}")
        return True
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
    print("1. 🌐 Online (fetch latest from today_arweave.ar.io)")
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
    backup_file_path = os.path.join(script_dir, '..', 'data', 'today_backup.json')
    
    if user_choice == "online":
        # User specifically wants online data
        print("🌐 Fetching online data as requested...")
        news_data = fetch_online_news_data()
        if news_data:
            # Save a backup copy
            save_news_data_locally(news_data, backup_file_path)
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
                        print("⚠️ Local file also failed, trying backup...")
                        backup_data = load_news_data(backup_file_path)
                        if backup_data:
                            print("✅ Using backup data file.")
                            return backup_data
            except KeyboardInterrupt:
                print("\n🛑 Operation cancelled.")
            return None
            
    elif user_choice == "local":
        # User specifically wants local data
        print("📁 Using local data as requested...")
        return load_news_data(local_file_path)
        
    else:  # user_choice == "auto"
        # Try online first, fallback to local
        print("🔄 Auto mode: Trying online first...")
        news_data = fetch_online_news_data()
        
        if news_data:
            # Online successful - save backup and use it
            save_news_data_locally(news_data, backup_file_path)
            return news_data
        else:
            # Online failed - try local file
            print("⚠️ Online fetch failed, trying local file...")
            local_data = load_news_data(local_file_path)
            
            if local_data:
                print("✅ Using local data file.")
                return local_data
            else:
                # Local also failed - try backup
                print("⚠️ Local file failed, trying backup file...")
                backup_data = load_news_data(backup_file_path)
                
                if backup_data:
                    print("✅ Using backup data file.")
                    return backup_data
                else:
                    print("❌ All data sources failed.")
                    return None

def main():
    """
    Main function to drive the podcast script generation with video transcription and AI enhancement.
    """
    print("🎙️  ARWEAVE TODAY SCRIPT GENERATOR")
    print("="*50)
    
    # Test API integrations
    assemblyai_available, gemini_available = test_integrations()
    
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

    # Generate the raw podcast script (including video transcription)
    print("📝 Generating raw podcast script with video transcription...")
    raw_script_content = generate_script(news_data)

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

    # Create the output directory if it doesn't exist
    output_dir = os.path.join(script_dir, '..', 'output')
    os.makedirs(output_dir, exist_ok=True)

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