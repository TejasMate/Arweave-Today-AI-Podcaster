"""
Video service for downloading and transcribing video content.

This module handles video downloading from URLs and transcription using Whisper AI.
"""

import os
import yt_dlp
from faster_whisper import WhisperModel
from datetime import datetime
from typing import Optional

from ..utils.config import config
from ..utils.file_utils import save_text_file, load_text_file, ensure_directory_exists


class VideoService:
    """Service for video downloading and transcription."""
    
    def __init__(self, output_dir: str):
        """
        Initialize the video service.
        
        Args:
            output_dir: Directory for saving transcripts and temporary files
        """
        self.output_dir = output_dir
        self.whisper_model = None
        ensure_directory_exists(output_dir)
    
    def _get_whisper_model(self) -> WhisperModel:
        """
        Get or initialize the Whisper model.
        
        Returns:
            WhisperModel instance
        """
        if self.whisper_model is None:
            print(f"📥 Loading Whisper model: {config.WHISPER_MODEL}")
            self.whisper_model = WhisperModel(config.WHISPER_MODEL)
        return self.whisper_model
    
    def transcribe_video(self, video_url: str, topic_identifier: Optional[str] = None) -> str:
        """
        Download audio from video URL and transcribe it using Whisper.
        
        Args:
            video_url: URL of the video to transcribe
            topic_identifier: Identifier for the topic (e.g., "topic_1")
            
        Returns:
            Transcribed text, or empty string if failed
        """
        try:
            print(f"\nAttempting to transcribe video: {video_url}")
            
            # Generate filename
            if topic_identifier:
                temp_audio_filename = f"{topic_identifier}_video"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_audio_filename = f"temp_audio_{timestamp}"
            
            # Check if transcript already exists
            transcript_filename = f"{temp_audio_filename}_transcript.txt"
            transcript_path = os.path.join(self.output_dir, transcript_filename)
            
            if os.path.exists(transcript_path):
                print(f"📄 Transcript file already exists: {transcript_filename}")
                print("⏭️  Skipping video download and transcription...")
                
                existing_content = load_text_file(transcript_path)
                if existing_content and not existing_content.startswith("[TRANSCRIPTION FAILED"):
                    print("✅ Using existing transcript")
                    return existing_content
                else:
                    print("⚠️  Existing transcript appears to be empty or failed, re-processing...")
            
            # Download and transcribe
            temp_audio_path_base = os.path.join(self.output_dir, temp_audio_filename)
            audio_path = self._download_audio(video_url, temp_audio_path_base)
            
            if not audio_path:
                return self._save_failed_transcript(transcript_path, "Audio download failed")
            
            transcript_text = self._transcribe_audio(audio_path)
            
            # Clean up temporary audio file
            try:
                os.remove(audio_path)
                print(f"🗑️  Cleaned up temporary audio file")
            except Exception as e:
                print(f"⚠️  Could not remove temporary file: {e}")
            
            # Save transcript
            if transcript_text:
                save_text_file(transcript_text, transcript_path)
                print(f"📄 Video transcript saved: {transcript_filename}")
                return transcript_text
            else:
                return self._save_failed_transcript(transcript_path, "Transcription failed")
                
        except Exception as e:
            print(f"⚠️ Error transcribing video {video_url}: {e}")
            if 'transcript_path' in locals():
                return self._save_failed_transcript(transcript_path, f"Error: {e}")
            return ""
    
    def _download_audio(self, video_url: str, output_path_base: str) -> Optional[str]:
        """
        Download audio from video URL.
        
        Args:
            video_url: URL to download from
            output_path_base: Base path for output file
            
        Returns:
            Path to downloaded audio file, or None if failed
        """
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{output_path_base}.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'extractaudio': True,
                'audioformat': 'wav',
                'audioquality': 0,
                'socket_timeout': 30,
                'retries': 3,
                'fragment_retries': 3,
            }
            
            # Add FFmpeg path if configured
            if config.FFMPEG_PATH:
                ydl_opts['ffmpeg_location'] = config.FFMPEG_PATH
            
            print(f"📥 Downloading audio from video...")
            print(f"🔗 URL: {video_url}")
            
            # Special handling for Twitter/X videos
            if 'twimg.com' in video_url or 'twitter.com' in video_url or 'x.com' in video_url:
                print("🐦 Detected Twitter/X video - using direct download")
                return self._download_direct_video(video_url, output_path_base)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                
                # Find the downloaded file
                for ext in ['wav', 'mp3', 'm4a', 'webm']:
                    potential_path = f"{output_path_base}.{ext}"
                    if os.path.exists(potential_path):
                        print(f"✅ Audio downloaded: {os.path.basename(potential_path)}")
                        return potential_path
                
                print("⚠️ Downloaded file not found")
                return None
                
        except Exception as e:
            print(f"⚠️ Error downloading audio: {e}")
            # Try direct download as fallback
            if 'twimg.com' in video_url:
                print("🔄 Trying direct download as fallback...")
                return self._download_direct_video(video_url, output_path_base)
            return None
    
    def _download_direct_video(self, video_url: str, output_path_base: str) -> Optional[str]:
        """
        Download video directly using requests for Twitter/X videos.
        
        Args:
            video_url: Direct video URL
            output_path_base: Base path for output file
            
        Returns:
            Path to downloaded video file, or None if failed
        """
        try:
            import requests
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            print("📥 Attempting direct video download...")
            response = requests.get(video_url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            
            # Determine file extension from URL or content type
            if video_url.endswith('.mp4'):
                ext = 'mp4'
            elif video_url.endswith('.webm'):
                ext = 'webm'
            else:
                ext = 'mp4'  # Default
            
            video_path = f"{output_path_base}.{ext}"
            
            # Download the video
            with open(video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ Video downloaded: {os.path.basename(video_path)}")
            
            # Extract audio using FFmpeg directly
            audio_path = f"{output_path_base}.wav"
            return self._extract_audio_with_ffmpeg(video_path, audio_path)
            
        except Exception as e:
            print(f"⚠️ Direct download failed: {e}")
            return None
    
    def _extract_audio_with_ffmpeg(self, video_path: str, audio_path: str) -> Optional[str]:
        """
        Extract audio from video using FFmpeg.
        
        Args:
            video_path: Path to video file
            audio_path: Path for output audio file
            
        Returns:
            Path to audio file if successful, None otherwise
        """
        try:
            import subprocess
            
            # FFmpeg command to extract audio
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit
                '-ar', '16000',  # Sample rate
                '-ac', '1',  # Mono
                '-y',  # Overwrite output file
                audio_path
            ]
            
            print("🎵 Extracting audio with FFmpeg...")
            
            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and os.path.exists(audio_path):
                print(f"✅ Audio extracted: {os.path.basename(audio_path)}")
                
                # Clean up video file
                try:
                    os.remove(video_path)
                    print("🗑️ Cleaned up video file")
                except:
                    pass
                
                return audio_path
            else:
                print(f"⚠️ FFmpeg failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("⚠️ FFmpeg timeout")
            return None
        except Exception as e:
            print(f"⚠️ FFmpeg error: {e}")
            return None
    
    def _transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio file using Whisper.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        try:
            print(f"🎤 Transcribing audio with Whisper ({config.WHISPER_MODEL})...")
            
            model = self._get_whisper_model()
            segments, info = model.transcribe(audio_path, language="en")
            
            transcript_text = ' '.join([segment.text.strip() for segment in segments])
            
            if transcript_text.strip():
                print(f"✅ Transcription completed ({len(transcript_text)} characters)")
                return transcript_text.strip()
            else:
                print("⚠️ Transcription resulted in empty text")
                return ""
                
        except Exception as e:
            print(f"⚠️ Error during transcription: {e}")
            return ""
    
    def _save_failed_transcript(self, transcript_path: str, error_message: str) -> str:
        """
        Save a failed transcript marker.
        
        Args:
            transcript_path: Path to save the failed transcript
            error_message: Error message to include
            
        Returns:
            Empty string
        """
        failed_content = f"[TRANSCRIPTION FAILED: {error_message}]"
        save_text_file(failed_content, transcript_path)
        return ""


# Factory function
def create_video_service(output_dir: str) -> VideoService:
    """
    Create a video service instance.
    
    Args:
        output_dir: Directory for output files
        
    Returns:
        VideoService instance
    """
    return VideoService(output_dir)
