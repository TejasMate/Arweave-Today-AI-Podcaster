"""
Tests for configuration utilities.
"""

import pytest
import os
from unittest.mock import patch
from arweave_podcaster.utils.config import Config


class TestConfig:
    """Test configuration management."""
    
    def test_default_values(self):
        """Test default configuration values."""
        # Test that defaults are reasonable
        assert Config.WHISPER_MODEL == 'tiny.en'
        assert Config.NEWS_SOURCE_URL == 'https://today_arweave.ar.io/'
        assert 'github.com' in Config.GITHUB_FALLBACK_URL
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key_123'})
    def test_is_gemini_configured_true(self):
        """Test Gemini configuration detection when key is set."""
        # Reload config to pick up environment change
        config = Config()
        config.GEMINI_API_KEY = 'test_key_123'
        
        assert config.is_gemini_configured() is True
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': ''})
    def test_is_gemini_configured_false(self):
        """Test Gemini configuration detection when key is empty."""
        config = Config()
        config.GEMINI_API_KEY = ''
        
        assert config.is_gemini_configured() is False
    
    def test_validate_config_missing_gemini(self):
        """Test configuration validation with missing Gemini key."""
        config = Config()
        config.GEMINI_API_KEY = ''
        
        missing = config.validate_config()
        
        assert len(missing) > 0
        assert any('GEMINI_API_KEY' in msg for msg in missing)
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'})
    def test_validate_config_complete(self):
        """Test configuration validation with all required keys."""
        config = Config()
        config.GEMINI_API_KEY = 'test_key'
        
        missing = config.validate_config()
        
        assert len(missing) == 0
    
    def test_get_output_dir(self):
        """Test output directory path generation."""
        base_dir = "/test/base"
        date_folder = "04-07-2025"
        
        output_dir = Config.get_output_dir(base_dir, date_folder)
        
        assert output_dir == "/test/base/output/04-07-2025"
    
    def test_get_data_dir(self):
        """Test data directory path generation."""
        base_dir = "/test/base"
        date_folder = "04-07-2025"
        
        data_dir = Config.get_data_dir(base_dir, date_folder)
        
        assert data_dir == "/test/base/data/04-07-2025"


if __name__ == "__main__":
    pytest.main([__file__])
