#!/usr/bin/env python3
"""
Test script for video download functionality.
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from arweave_podcaster.services.video_service import VideoService
from arweave_podcaster.utils.file_utils import load_json_file

def test_video_download():
    """Test video download with sample data."""
    print("🧪 Testing video download functionality...")
    
    # Load sample data
    data_path = "/workspaces/arweave/data/04-07-2025/today.json"
    news_data = load_json_file(data_path)
    
    if not news_data:
        print("❌ Could not load test data")
        return False
    
    # Find a topic with video
    video_topic = None
    for topic in news_data.get('topics', []):
        if 'video' in topic:
            video_topic = topic
            break
    
    if not video_topic:
        print("❌ No video topic found in test data")
        return False
    
    print(f"🎬 Testing with video: {video_topic['video']}")
    
    # Create video service
    test_dir = "/tmp/arweave_video_test"
    os.makedirs(test_dir, exist_ok=True)
    
    video_service = VideoService(test_dir)
    
    # Test transcription
    try:
        transcript = video_service.transcribe_video(video_topic['video'], "test_video")
        
        if transcript and not transcript.startswith("[TRANSCRIPTION FAILED"):
            print("✅ Video transcription successful!")
            print(f"📄 Transcript length: {len(transcript)} characters")
            print(f"📄 First 100 chars: {transcript[:100]}...")
            return True
        else:
            print(f"❌ Transcription failed: {transcript}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_video_download()
    sys.exit(0 if success else 1)
