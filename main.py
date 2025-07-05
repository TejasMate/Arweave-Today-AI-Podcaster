#!/usr/bin/env python3
"""
Command-line interface for Arweave Today Podcast Generator.

This script provides a convenient entry point for running the podcast generator.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from arweave_podcaster.core.podcast_generator import main

if __name__ == "__main__":
    main()
