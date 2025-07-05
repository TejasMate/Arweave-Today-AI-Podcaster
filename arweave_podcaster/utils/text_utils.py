"""
Text processing utilities for Arweave Podcaster.

This module contains functions for cleaning and processing text content for audio generation.
"""

import re
from typing import List, Dict, Any


def clean_script_for_audio(script_text: str) -> str:
    """
    Cleans the script text for audio generation by removing stage directions, 
    formatting elements, and other text that shouldn't be read aloud.
    
    Args:
        script_text: The raw script text with formatting elements
        
    Returns:
        Cleaned text suitable for text-to-speech conversion
    """
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


def format_news_topics(topics: List[Dict[str, Any]]) -> str:
    """
    Format news topics into readable text for podcast script.
    
    Args:
        topics: List of topic dictionaries from news data
        
    Returns:
        Formatted text string
    """
    formatted_sections = []
    
    for i, topic in enumerate(topics, 1):
        nature = topic.get('nature', 'news').title()
        headline = topic.get('headline', 'No headline')
        body = topic.get('body', 'No content available')
        
        # Create section header
        if i == 1:
            section_text = f"First up, in {nature.lower()} news: {body}"
        elif i == len(topics):
            section_text = f"And finally, in {nature.lower()} news: {body}"
        else:
            section_text = f"Moving to {nature.lower()} news: {body}"
        
        formatted_sections.append(section_text)
    
    return "\n\n".join(formatted_sections)


def format_chitchat_section(chitchat: Dict[str, Any]) -> str:
    """
    Format chitchat section for podcast script.
    
    Args:
        chitchat: Chitchat dictionary from news data
        
    Returns:
        Formatted chitchat text
    """
    nature = chitchat.get('nature', 'Did you know?')
    headline = chitchat.get('headline', '')
    body = chitchat.get('body', '')
    
    if headline and body:
        return f"{nature} {headline}. {body}"
    elif headline:
        return f"{nature} {headline}."
    elif body:
        return f"{nature} {body}"
    else:
        return ""


def format_suggested_read(suggested: Dict[str, Any]) -> str:
    """
    Format suggested reading section for podcast script.
    
    Args:
        suggested: Suggested reading dictionary from news data
        
    Returns:
        Formatted suggested reading text
    """
    nature = suggested.get('nature', "today's read")
    headline = suggested.get('headline', '')
    body = suggested.get('body', '')
    
    intro = f"For {nature}, we recommend checking out"
    
    if headline and body:
        return f"{intro} '{headline}'. {body}"
    elif headline:
        return f"{intro} '{headline}'."
    elif body:
        return f"{intro}: {body}"
    else:
        return ""


def create_podcast_opening(date_str: str) -> str:
    """
    Create the opening for the podcast.
    
    Args:
        date_str: Date string for the podcast
        
    Returns:
        Opening text
    """
    return f"Welcome to Arweave Today for {date_str}. Here are the latest updates from across the arweave ecosystem."


def create_podcast_closing() -> str:
    """
    Create the closing for the podcast.
    
    Returns:
        Closing text
    """
    return "That's all for Arweave Today. Thanks for listening."
