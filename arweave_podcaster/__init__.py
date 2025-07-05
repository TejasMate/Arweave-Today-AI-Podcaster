"""
Arweave Today AI Podcaster

An intelligent, automated podcast generator that transforms Arweave ecosystem news 
into professional-quality audio content.
"""

__version__ = "1.0.0"
__author__ = "Arweave Ecosystem"
__email__ = "contact@arweave.org"

from .core.podcast_generator import PodcastGenerator
from .services.gemini_service import GeminiService
from .services.data_service import DataService

__all__ = ["PodcastGenerator", "GeminiService", "DataService"]
