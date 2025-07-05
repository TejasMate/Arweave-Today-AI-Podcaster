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
            }
            
            # Add FFmpeg path if configured
            if config.FFMPEG_PATH:
                ydl_opts['ffmpeg_location'] = config.FFMPEG_PATH
            
            print(f"📥 Downloading audio from video...")
            
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
