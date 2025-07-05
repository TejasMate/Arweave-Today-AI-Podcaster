"""
Tests for text utilities.
"""

import pytest
from arweave_podcaster.utils.text_utils import (
    clean_script_for_audio, 
    format_news_topics,
    create_podcast_opening,
    create_podcast_closing
)


class TestTextUtils:
    """Test text processing utilities."""
    
    def test_clean_script_for_audio(self):
        """Test script cleaning for audio generation."""
        raw_script = """
        **Host:** Welcome to the show!
        
        (music fades in)
        This is the main content.
        (sound effect: applause)
        
        **Host:** That's all for today.
        """
        
        cleaned = clean_script_for_audio(raw_script)
        
        assert "**Host:**" not in cleaned
        assert "(music fades in)" not in cleaned
        assert "(sound effect: applause)" not in cleaned
        assert "Welcome to the show!" in cleaned
        assert "This is the main content." in cleaned
    
    def test_create_podcast_opening(self):
        """Test podcast opening generation."""
        date_str = "July 04, 2025"
        opening = create_podcast_opening(date_str)
        
        assert "Welcome to Arweave Today" in opening
        assert date_str in opening
        assert "permaweb ecosystem" in opening
    
    def test_create_podcast_closing(self):
        """Test podcast closing generation."""
        closing = create_podcast_closing()
        
        assert "That's all for Arweave Today" in closing
        assert "Thanks for listening" in closing
    
    def test_format_news_topics(self):
        """Test news topics formatting."""
        topics = [
            {
                "nature": "funding",
                "headline": "Test Grant",
                "body": "Some project received funding."
            },
            {
                "nature": "community",
                "headline": "Community Update",
                "body": "Community news here."
            }
        ]
        
        formatted = format_news_topics(topics)
        
        assert "First up, in funding news:" in formatted
        assert "And finally, in community news:" in formatted
        assert "Some project received funding." in formatted
        assert "Community news here." in formatted


if __name__ == "__main__":
    pytest.main([__file__])
