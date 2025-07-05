#!/usr/bin/env python3
"""
Gemini AI Test Script for Podcast Script Enhancement
Tests Gemini API integration and script generation capabilities.
"""

import os
import sys
from datetime import datetime

# Add the src directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import google.generativeai as genai
except ImportError:
    print("❌ Error: google-generativeai not installed")
    print("Please install it with: pip install google-generativeai")
    sys.exit(1)

# Configuration
GEMINI_API_KEY = "AIzaSyAbsUcEy287kZqJ5-xT57247PppkkEt2Ws"  # Replace with your actual API key

class GeminiTester:
    """
    Test class for Gemini AI functionality with podcast script generation.
    """
    
    def __init__(self, api_key: str):
        """Initialize Gemini with API key."""
        self.api_key = api_key
        self.model = None
        
        if api_key == "your_gemini_api_key_here":
            print("❌ Please set your actual Gemini API key in GEMINI_API_KEY")
            return
            
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            print("✅ Gemini AI initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Gemini: {e}")
    
    def test_basic_connection(self):
        """Test basic Gemini API connection."""
        if not self.model:
            return False
            
        try:
            print("\n🔗 Testing basic connection...")
            response = self.model.generate_content("Hello! Please respond with 'Connection successful'")
            
            if response and response.text:
                print(f"✅ Connection test successful: {response.text.strip()}")
                return True
            else:
                print("❌ Connection test failed: Empty response")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def test_podcast_script_generation(self, sample_raw_content: str):
        """Test podcast script generation with sample content."""
        if not self.model:
            return None
            
        try:
            print("\n🎙️ Testing podcast script generation...")
            
            prompt = f"""
You are a professional podcast script writer for "Arweave Today," a daily news podcast about the Arweave ecosystem and decentralized web technologies.

Transform the following raw content into a polished, engaging podcast script:

GUIDELINES:
1. Create a natural, conversational flow suitable for audio
2. Use clear transitions between topics
3. Explain technical terms in accessible language
4. Maintain an enthusiastic but professional tone
5. Keep the existing structure: Welcome → Main Stories → Did You Know → Suggested Read → Outro
6. When video transcripts are included, summarize key points naturally rather than reading verbatim
7. Make it sound like a human host is speaking, not reading a script
8. Include natural pauses and emphasis cues with punctuation
9. Keep segments concise and engaging
10. Maintain the technical accuracy while improving readability

RAW CONTENT:
{sample_raw_content}

Generate a professional podcast script that flows naturally when spoken aloud. Focus on making it conversational and engaging for listeners interested in Arweave and decentralized technologies.
"""

            response = self.model.generate_content(prompt)
            
            if response and response.text:
                print("✅ Podcast script generation successful!")
                return response.text.strip()
            else:
                print("❌ Script generation failed: Empty response")
                return None
                
        except Exception as e:
            print(f"❌ Script generation failed: {e}")
            return None
    
    def save_test_results(self, original_content: str, enhanced_content: str):
        """Save test results to files for comparison."""
        try:
            # Create test output directory
            test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output', 'gemini_test')
            os.makedirs(test_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save original content
            original_file = os.path.join(test_dir, f"original_content_{timestamp}.txt")
            with open(original_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Save enhanced content
            enhanced_file = os.path.join(test_dir, f"gemini_enhanced_{timestamp}.txt")
            with open(enhanced_file, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
            
            print(f"\n💾 Test results saved:")
            print(f"📄 Original: {os.path.basename(original_file)}")
            print(f"🤖 Enhanced: {os.path.basename(enhanced_file)}")
            print(f"📁 Location: {test_dir}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving test results: {e}")
            return False

def load_sample_content():
    """Load sample content for testing."""
    # You can modify this to load from the actual file or use sample content
    sample_content = """
Welcome to Arweave Today for July 04, 2025.
Here are the latest updates from across the permaweb ecosystem.
--------------------
MAIN STORIES:
In ao computer news: Berlin Recap: AOS on HyperBEAM.
Forward Research CTO Tom Wilson took the stage at Arweave Day Berlin to discuss AOS, the operating system at the heart of the AO Computer. His talk explored the origins of AOS, its current capabilities, and what's next as the system continues to evolve.

[Video Transcript]:
We've been building nonstop. It's been a fantastic week here and I'm super excited about what we're doing and where we're going to go. AOS is different than your typical kind of stack of tools. The first thing I thought of was, hey, Claude, why don't you create a talk? Message first architecture, everything's a message, right? We send messages back and forth, which is a little bit different than the norm, holographic state.

In developer news: ARIO Gateway Services Overview.
David Whittington recently shared a clear breakdown of the vital role gateways play in the ARIO network. Gateway nodes ensure access to the permaweb by providing key services like data caching and chain, bundle, and data indexing.

--------------------
DID YOU KNOW?:
Arweave's endowment holds over 240,000 $AR: This long-term funding mechanism ensures miner incentives remain strong, only releasing tokens if regular block rewards fall short of covering permanent data storage.
--------------------
TODAY'S SUGGESTED READ:
'Permaweb Goes IRL: Bazar in NYC'.
If you'd like to learn more about Arweave's presence at NFT.NYC, check out this write-up in the Permaweb Journal.
--------------------
That's all for Arweave Today. Thanks for listening.
"""
    return sample_content.strip()

def load_actual_content():
    """Load actual content from the generated file."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        content_file = os.path.join(script_dir, '..', 'output', 'ArweaveToday-2025-07-03.txt')
        
        if os.path.exists(content_file):
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ Loaded actual content from: {os.path.basename(content_file)}")
            return content
        else:
            print("⚠️ Actual content file not found, using sample content")
            return None
            
    except Exception as e:
        print(f"⚠️ Error loading actual content: {e}")
        return None

def main():
    """Main test function."""
    print("🎙️ GEMINI AI PODCAST SCRIPT TESTER")
    print("=" * 50)
    
    # Initialize Gemini tester
    tester = GeminiTester(GEMINI_API_KEY)
    
    if not tester.model:
        print("❌ Cannot proceed without valid Gemini configuration")
        return
    
    # Test basic connection
    if not tester.test_basic_connection():
        print("❌ Basic connection failed, cannot proceed")
        return
    
    # Load content for testing
    print("\n📖 Loading content for testing...")
    
    # Try to load actual content first, fall back to sample
    content = load_actual_content()
    if not content:
        content = load_sample_content()
        print("📄 Using sample content for testing")
    
    # Test podcast script generation
    enhanced_content = tester.test_podcast_script_generation(content)
    
    if enhanced_content:
        # Save results
        tester.save_test_results(content, enhanced_content)
        
        # Show preview of results
        print(f"\n📊 COMPARISON PREVIEW:")
        print("=" * 50)
        print("📄 ORIGINAL (first 200 chars):")
        print(content[:200] + "...")
        print("\n🤖 GEMINI ENHANCED (first 200 chars):")
        print(enhanced_content[:200] + "...")
        print("=" * 50)
        
        print(f"\n✅ TEST COMPLETED SUCCESSFULLY!")
        print("🎯 Gemini AI is working properly for podcast script enhancement")
        
    else:
        print("\n❌ TEST FAILED!")
        print("Script generation did not work as expected")

if __name__ == "__main__":
    main()
