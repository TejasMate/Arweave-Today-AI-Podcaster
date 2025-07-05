#!/usr/bin/env python3
"""
Command-line interface for Arweave Today Podcast Generator.

This script provides a convenient entry point for running the podcast generator.
"""

import sys
import os
import argparse

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from arweave_podcaster.core.podcast_generator import main

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate AI podcast from Arweave news data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Interactive mode - choose data source
  python main.py -f data/today.json       # Generate from specific JSON file
  python main.py --file data/04-07-2025/today.json  # Generate from dated file
        """
    )
    
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="Path to JSON file containing news data for podcast generation"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Arweave Today Podcast Generator 1.0.0"
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(json_file=args.file)
