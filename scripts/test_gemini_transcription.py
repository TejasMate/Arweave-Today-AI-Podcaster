#!/usr/bin/env python3
"""
Test script for Google Gemini audio transcription.

This script demonstrates how to use Google Gemini AI to transcribe audio files.
It's designed for testing purposes and can be used to validate the transcription quality.

Usage:
    python scripts/test_gemini_transcription.py [audio_file_path]

Requirements:
    - GEMINI_API_KEY environment variable set
    - Audio file for testing (MP3, WAV, etc.)
    - google-generativeai library
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from arweave_podcaster.services.gemini_service import GeminiService
from arweave_podcaster.utils.config import Config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GeminiTranscriptionTester:
    """Test class for Gemini audio transcription."""
    
    def __init__(self):
        """Initialize the tester with Gemini service."""
        self.gemini_service = GeminiService(Config.GEMINI_API_KEY)
        
    async def test_audio_transcription(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """
        Test audio transcription using Gemini.
        
        Args:
            audio_path: Path to the audio file to transcribe
            
        Returns:
            Dictionary containing transcription results or None if failed
        """
        try:
            audio_file = Path(audio_path)
            if not audio_file.exists():
                logger.error(f"Audio file not found: {audio_path}")
                return None
                
            # Check if file has a valid audio extension
            valid_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac'}
            if audio_file.suffix.lower() not in valid_extensions:
                logger.error(f"File is not a supported audio format: {audio_path}")
                return None
                
            logger.info(f"Starting transcription of: {audio_file.name}")
            logger.info(f"File size: {audio_file.stat().st_size / 1024 / 1024:.2f} MB")
            
            # Create a simple, clear prompt for transcription
            transcription_prompt = """
            Please transcribe this audio file accurately. Provide a clear, word-for-word transcription of the spoken content.
            
            Requirements:
            - Accurate transcription of all spoken words
            - Proper punctuation and formatting
            - If certain words are unclear, use [inaudible] or [unclear]
            - Maintain natural paragraph breaks for readability
            
            Focus on accuracy and clarity in the transcription.
            """
            
            # Perform transcription
            result = await self.gemini_service.transcribe_audio_file(
                audio_path=str(audio_file),
                prompt=transcription_prompt
            )
            
            if result:
                logger.info("Transcription completed successfully!")
                return {
                    'file_path': str(audio_file),
                    'file_size_mb': audio_file.stat().st_size / 1024 / 1024,
                    'transcription': result,
                    'status': 'success'
                }
            else:
                logger.error("Transcription failed - no result returned")
                return {
                    'file_path': str(audio_file),
                    'status': 'failed',
                    'error': 'No transcription result'
                }
                
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            return {
                'file_path': audio_path,
                'status': 'error',
                'error': str(e)
            }
    
    def save_transcription_result(self, result: Dict[str, Any], output_dir: str = "output/test_transcriptions") -> None:
        """
        Save transcription result to a file.
        
        Args:
            result: Transcription result dictionary
            output_dir: Directory to save the result
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            audio_name = Path(result['file_path']).stem
            output_file = output_path / f"{audio_name}_transcription.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"=== GEMINI AUDIO TRANSCRIPTION TEST ===\n")
                f.write(f"File: {result['file_path']}\n")
                f.write(f"Status: {result['status']}\n")
                
                if 'file_size_mb' in result:
                    f.write(f"Size: {result['file_size_mb']:.2f} MB\n")
                
                f.write(f"Timestamp: {asyncio.get_event_loop().time()}\n")
                f.write("=" * 50 + "\n\n")
                
                if result['status'] == 'success':
                    f.write("TRANSCRIPTION:\n")
                    f.write("-" * 30 + "\n")
                    f.write(result['transcription'])
                else:
                    f.write("ERROR:\n")
                    f.write("-" * 10 + "\n")
                    f.write(result.get('error', 'Unknown error'))
                
                f.write("\n\n" + "=" * 50 + "\n")
            
            logger.info(f"Transcription result saved to: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save transcription result: {str(e)}")


def create_sample_audio_info():
    """Print information about creating a sample audio file for testing."""
    print("\n" + "="*60)
    print("SAMPLE AUDIO CREATION FOR TESTING")
    print("="*60)
    print("To test this script, you need an audio file. Here are some options:")
    print()
    print("1. **Record sample audio:**")
    print("   - Use your phone or computer to record 1-2 minutes of speech")
    print("   - Save in MP3, WAV, or other supported format")
    print("   - Speak clearly for best transcription results")
    print()
    print("2. **Convert existing media:**")
    print("   - Extract audio from video using ffmpeg:")
    print("   - ffmpeg -i input_video.mp4 -q:a 0 -map a output_audio.mp3")
    print()
    print("3. **Use online sources:**")
    print("   - Download a podcast episode (check licensing)")
    print("   - Use royalty-free audio content")
    print()
    print("4. **Supported formats:**")
    print("   - MP3, WAV, M4A, FLAC, OGG, AAC")
    print()
    print("RECOMMENDED: Record a 1-2 minute speech sample for testing!")
    print("="*60)


async def main():
    """Main function to run the transcription test."""
    # Check for API key
    if not Config.is_gemini_configured():
        logger.error("GEMINI_API_KEY environment variable not set!")
        print("\nPlease set your Gemini API key:")
        print("export GEMINI_API_KEY='your-api-key-here'")
        return
    
    # Check for audio file argument
    if len(sys.argv) < 2:
        logger.error("No audio file provided!")
        print("\nUsage: python scripts/test_gemini_transcription.py <audio_file_path>")
        print("Example: python scripts/test_gemini_transcription.py /path/to/audio.mp3")
        create_sample_audio_info()
        return
    
    audio_path = sys.argv[1]
    
    # Initialize tester
    tester = GeminiTranscriptionTester()
    
    print(f"\n🎵 Testing Gemini Audio Transcription")
    print(f"📁 File: {audio_path}")
    print("🚀 Starting transcription...\n")
    
    # Run transcription test
    result = await tester.test_audio_transcription(audio_path)
    
    if result:
        # Save result to file
        tester.save_transcription_result(result)
        
        # Print summary
        print("\n" + "="*60)
        print("TRANSCRIPTION TEST RESULTS")
        print("="*60)
        print(f"Status: {result['status']}")
        
        if result['status'] == 'success':
            print(f"✅ Transcription completed successfully!")
            print(f"📝 Length: {len(result['transcription'])} characters")
            print("\n📋 TRANSCRIPTION PREVIEW:")
            print("-" * 40)
            # Show first 500 characters of transcription
            preview = result['transcription'][:500]
            if len(result['transcription']) > 500:
                preview += "..."
            print(preview)
            print("-" * 40)
        else:
            print(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
        
        print("="*60)
    else:
        print("❌ Failed to get transcription result")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
