"""
Configuration management for Arweave Podcaster.

This module handles loading and managing environment variables and application settings.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


class Config:
    """Configuration class for managing application settings."""
    
    # FFmpeg configuration
    FFMPEG_PATH: str = os.getenv('FFMPEG_PATH', '')
    
    # Whisper model configuration
    WHISPER_MODEL: str = os.getenv('WHISPER_MODEL', 'tiny.en')
    
    # Data Source Configuration
    NEWS_SOURCE_URL: str = os.getenv('NEWS_SOURCE_URL', 'https://today_arweave.ar.io/')
    GITHUB_FALLBACK_URL: str = os.getenv('GITHUB_FALLBACK_URL', 
                                         'https://raw.githubusercontent.com/ArweaveTeam/arweave-today/main/data/today.json')
    
    # Gemini AI Configuration
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    ENABLE_GEMINI_SCRIPT_GENERATION: bool = os.getenv('ENABLE_GEMINI_SCRIPT_GENERATION', 'True').lower() == 'true'
    
    @classmethod
    def is_gemini_configured(cls) -> bool:
        """Check if Gemini API is properly configured."""
        return bool(cls.GEMINI_API_KEY and cls.GEMINI_API_KEY.strip())
    
    @classmethod
    def validate_config(cls) -> list[str]:
        """Validate configuration and return list of missing required settings."""
        missing = []
        
        if not cls.is_gemini_configured():
            missing.append("GEMINI_API_KEY is required for AI features")
            
        return missing
    
    @classmethod
    def get_output_dir(cls, base_dir: str, date_folder: str) -> str:
        """Get the output directory path for a given date."""
        return os.path.join(base_dir, 'output', date_folder)
    
    @classmethod
    def get_data_dir(cls, base_dir: str, date_folder: str) -> str:
        """Get the data directory path for a given date."""
        return os.path.join(base_dir, 'data', date_folder)


# Create a singleton instance
config = Config()
