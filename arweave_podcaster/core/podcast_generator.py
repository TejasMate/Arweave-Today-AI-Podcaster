"""
Main podcast generator class.

This module contains the core PodcastGenerator class that orchestrates the entire
podcast generation process.
"""

import os
from typing import Dict, Any, Optional, List

from ..services.data_service import DataService, get_user_choice_for_data_source
from ..services.gemini_service import GeminiService, create_gemini_service
from ..services.video_service import VideoService, create_video_service
from ..utils.config import config
from ..utils.file_utils import (
    get_date_folder_from_timestamp, get_formatted_date_from_timestamp,
    get_datestamp_from_timestamp, create_output_filename, save_text_file,
    ensure_directory_exists
)
from ..utils.text_utils import (
    clean_script_for_audio, format_news_topics, format_chitchat_section,
    format_suggested_read, create_podcast_opening, create_podcast_closing
)


class PodcastGenerator:
    """Main class for generating podcasts from Arweave news data."""
    
    def __init__(self, base_dir: str):
        """
        Initialize the podcast generator.
        
        Args:
            base_dir: Base directory for the project
        """
        self.base_dir = base_dir
        self.data_service = DataService(base_dir)
        self.gemini_service: Optional[GeminiService] = None
        self.video_service: Optional[VideoService] = None
        
        # Test and initialize services
        self._initialize_services()
    
    def _initialize_services(self) -> None:
        """Initialize available services."""
        print("🔧 Initializing services...")
        
        # Initialize Gemini service
        if config.is_gemini_configured():
            self.gemini_service = create_gemini_service()
            if self.gemini_service and self.gemini_service.test_connection():
                print("✅ Gemini AI service initialized")
            else:
                print("❌ Gemini AI service failed to initialize")
                self.gemini_service = None
        else:
            print("⚠️ Gemini AI not configured")
    
    def generate_podcast(self, user_choice: str = "auto") -> bool:
        """
        Generate a complete podcast from news data.
        
        Args:
            user_choice: Data source choice ('online', 'local', 'auto')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print("🎙️  ARWEAVE TODAY PODCAST GENERATOR")
            print("="*50)
            
            # Load news data
            news_data = self.data_service.load_news_data_smart(user_choice)
            if not news_data:
                print("❌ No news data available")
                return False
            
            # Setup output directories
            timestamp_ms = news_data.get('ts', 0)
            date_folder = get_date_folder_from_timestamp(timestamp_ms)
            date_str = get_formatted_date_from_timestamp(timestamp_ms)
            datestamp = get_datestamp_from_timestamp(timestamp_ms)
            
            output_dir = config.get_output_dir(self.base_dir, date_folder)
            ensure_directory_exists(output_dir)
            
            print(f"📁 Output directory: output/{date_folder}")
            
            # Initialize video service for this generation
            self.video_service = create_video_service(output_dir)
            
            # Generate raw script
            print("📝 Generating raw podcast script...")
            raw_script = self._generate_raw_script(news_data, date_str)
            
            # Enhance script with AI if available
            if self.gemini_service and config.ENABLE_GEMINI_SCRIPT_GENERATION:
                print("🤖 Enhancing script with Gemini AI...")
                final_script = self.gemini_service.generate_podcast_script(raw_script, date_str)
            else:
                print("📄 Using raw script (AI enhancement not available)")
                final_script = raw_script
            
            # Save scripts
            base_filename = "ArweaveToday"
            raw_filename = create_output_filename(base_filename, datestamp, "raw.txt")
            final_filename = create_output_filename(base_filename, datestamp, "txt")
            audio_filename = create_output_filename(base_filename, datestamp, "wav")
            
            raw_path = os.path.join(output_dir, raw_filename)
            final_path = os.path.join(output_dir, final_filename)
            audio_path = os.path.join(output_dir, audio_filename)
            
            print("💾 Saving scripts...")
            save_text_file(raw_script, raw_path)
            save_text_file(final_script, final_path)
            
            # Generate audio
            if self.gemini_service:
                print("🎤 Generating podcast audio...")
                cleaned_script = clean_script_for_audio(final_script)
                success = self.gemini_service.generate_audio(cleaned_script, audio_path)
                if not success:
                    print("⚠️ Audio generation failed")
            else:
                print("⚠️ Audio generation skipped (Gemini not available)")
                success = False
            
            # Print summary
            self._print_generation_summary(output_dir, raw_filename, final_filename, 
                                         audio_filename if success else None)
            
            return True
            
        except Exception as e:
            print(f"❌ Error during podcast generation: {e}")
            return False
    
    def generate_podcast_from_file(self, json_file_path: str) -> Optional[str]:
        """
        Generate a podcast directly from a JSON file.
        
        Args:
            json_file_path: Path to the JSON file containing news data
            
        Returns:
            Output directory path if successful, None otherwise
        """
        try:
            # Load news data from file
            import json
            
            if not os.path.exists(json_file_path):
                print(f"❌ JSON file not found: {json_file_path}")
                return False
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            
            print(f"✅ Loaded news data from: {json_file_path}")
            
            # Setup output directories
            timestamp_ms = news_data.get('ts', 0)
            date_folder = get_date_folder_from_timestamp(timestamp_ms)
            date_str = get_formatted_date_from_timestamp(timestamp_ms)
            datestamp = get_datestamp_from_timestamp(timestamp_ms)
            
            output_dir = config.get_output_dir(self.base_dir, date_folder)
            ensure_directory_exists(output_dir)
            
            print(f"📁 Output directory: output/{date_folder}")
            
            # Initialize video service for this generation
            self.video_service = create_video_service(output_dir)
            
            # Generate raw script
            print("📝 Generating raw podcast script...")
            raw_script = self._generate_raw_script(news_data, date_str)
            
            # Enhance script with AI if available
            if self.gemini_service and config.ENABLE_GEMINI_SCRIPT_GENERATION:
                print("🤖 Enhancing script with Gemini AI...")
                final_script = self.gemini_service.generate_podcast_script(raw_script, date_str)
            else:
                print("📄 Using raw script (AI enhancement not available)")
                final_script = raw_script
            
            # Save scripts
            base_filename = "ArweaveToday"
            raw_filename = create_output_filename(base_filename, datestamp, "raw.txt")
            final_filename = create_output_filename(base_filename, datestamp, "txt")
            audio_filename = create_output_filename(base_filename, datestamp, "wav")
            
            raw_path = os.path.join(output_dir, raw_filename)
            final_path = os.path.join(output_dir, final_filename)
            audio_path = os.path.join(output_dir, audio_filename)
            
            print("💾 Saving scripts...")
            save_text_file(raw_script, raw_path)
            save_text_file(final_script, final_path)
            
            # Generate audio
            if self.gemini_service:
                print("🎤 Generating podcast audio...")
                cleaned_script = clean_script_for_audio(final_script)
                success = self.gemini_service.generate_audio(cleaned_script, audio_path)
                if not success:
                    print("⚠️ Audio generation failed")
            else:
                print("⚠️ Audio generation skipped (Gemini not available)")
                success = False
            
            # Print summary
            self._print_generation_summary(output_dir, raw_filename, final_filename, 
                                         audio_filename if success else None)
            
            return output_dir
            
        except Exception as e:
            print(f"❌ Error processing JSON file: {e}")
            return None

    def _generate_raw_script(self, news_data: Dict[str, Any], date_str: str) -> str:
        """
        Generate the raw podcast script from news data.
        
        Args:
            news_data: Dictionary containing news data
            date_str: Formatted date string
            
        Returns:
            Raw script text
        """
        script_parts = []
        
        # Opening
        script_parts.append(create_podcast_opening(date_str))
        script_parts.append("")
        
        # Process topics with video transcription
        topics = news_data.get('topics', [])
        if topics:
            topics_content = self._process_topics_with_videos(topics)
            script_parts.append(topics_content)
            script_parts.append("")
        
        # Chitchat section
        chitchat = news_data.get('chitchat', {})
        if chitchat:
            chitchat_content = format_chitchat_section(chitchat)
            if chitchat_content:
                script_parts.append(chitchat_content)
                script_parts.append("")
        
        # Suggested reading
        suggested = news_data.get('suggested', {})
        if suggested:
            suggested_content = format_suggested_read(suggested)
            if suggested_content:
                script_parts.append(suggested_content)
                script_parts.append("")
        
        # Closing
        script_parts.append(create_podcast_closing())
        
        return "\n".join(script_parts)
    
    def _process_topics_with_videos(self, topics: List[Dict[str, Any]]) -> str:
        """
        Process topics and transcribe any embedded videos.
        
        Args:
            topics: List of topic dictionaries
            
        Returns:
            Formatted topics content with video transcriptions
        """
        enhanced_topics = []
        
        for i, topic in enumerate(topics):
            enhanced_topic = topic.copy()
            
            # Check for video content
            video_url = topic.get('video')
            if video_url and self.video_service:
                topic_id = f"topic_{i+1}"
                transcript = self.video_service.transcribe_video(video_url, topic_id)
                
                if transcript:
                    # Append transcript to body
                    current_body = enhanced_topic.get('body', '')
                    enhanced_topic['body'] = f"{current_body}\n\nVideo content: {transcript}"
            
            enhanced_topics.append(enhanced_topic)
        
        return format_news_topics(enhanced_topics)
    
    def _print_generation_summary(self, output_dir: str, raw_filename: str, 
                                final_filename: str, audio_filename: Optional[str]) -> None:
        """
        Print generation summary.
        
        Args:
            output_dir: Output directory path
            raw_filename: Raw script filename
            final_filename: Final script filename
            audio_filename: Audio filename or None if not generated
        """
        print("\n" + "="*50)
        print("✅ PODCAST GENERATION COMPLETE!")
        print("="*50)
        print(f"📄 Raw Script: {raw_filename}")
        print(f"🎯 Final Script: {final_filename}")
        if audio_filename:
            print(f"🎵 Audio File: {audio_filename}")
        print(f"📁 Location: {output_dir}")
        
        if self.gemini_service:
            print("🤖 Enhanced with Gemini AI")
        
        print("="*50)


def main(json_file: Optional[str] = None) -> None:
    """Main entry point for the podcast generator."""
    try:
        # Get base directory (project root)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.dirname(script_dir))  # Go up to project root
        
        # Create generator
        generator = PodcastGenerator(base_dir)
        
        if json_file:
            # Direct JSON file mode
            print(f"📁 Using provided JSON file: {json_file}")
            output_dir = generator.generate_podcast_from_file(json_file)
            success = output_dir is not None
        else:
            # Interactive mode - get user choice for data source
            user_choice = get_user_choice_for_data_source()
            success = generator.generate_podcast(user_choice)
        
        if not success:
            print("❌ Podcast generation failed")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
