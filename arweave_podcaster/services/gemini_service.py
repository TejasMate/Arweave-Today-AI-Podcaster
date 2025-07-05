"""
Gemini AI service for script generation and text-to-speech.

This module handles all interactions with Google's Gemini AI API.
"""

import google.generativeai as genai
from google import genai as google_genai
from google.genai import types
from typing import Optional

from ..utils.config import config
from ..utils.audio_utils import save_binary_file, convert_to_wav, ensure_wav_extension


class GeminiService:
    """Service for Gemini AI script generation and TTS."""
    
    def __init__(self, api_key: str):
        """
        Initialize the Gemini service.
        
        Args:
            api_key: Gemini API key
        """
        self.api_key = api_key
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Gemini client."""
        try:
            genai.configure(api_key=self.api_key)
            self.client = google_genai.Client(api_key=self.api_key)
        except Exception as e:
            print(f"⚠️ Error initializing Gemini client: {e}")
    
    def test_connection(self) -> bool:
        """
        Test the connection to Gemini API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Hello, this is a test.")
            return response and response.text
        except Exception as e:
            print(f"⚠️ Gemini connection test failed: {e}")
            return False
    
    def generate_podcast_script(self, raw_content: str, date_str: str) -> str:
        """
        Generate an enhanced podcast script using Gemini AI.
        
        Args:
            raw_content: Raw news content to enhance
            date_str: Date string for the podcast
            
        Returns:
            Enhanced podcast script
        """
        try:
            print("🤖 Generating enhanced podcast script with Gemini AI...")
            
            prompt = self._create_script_enhancement_prompt(raw_content, date_str)
            
            model = genai.GenerativeModel(
                'gemini-1.5-flash',
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=8192,
                )
            )
            
            response = model.generate_content(prompt)
            
            if response and response.text:
                enhanced_script = response.text.strip()
                print("✅ Gemini AI script enhancement completed")
                return enhanced_script
            else:
                print("⚠️ No response from Gemini AI")
                return raw_content
                
        except Exception as e:
            print(f"⚠️ Error generating script with Gemini AI: {e}")
            return raw_content
    
    def _create_script_enhancement_prompt(self, raw_content: str, date_str: str) -> str:
        """
        Create the prompt for script enhancement.
        
        Args:
            raw_content: Raw content to enhance
            date_str: Date string for context
            
        Returns:
            Formatted prompt string
        """
        return f'''Transform this raw Arweave ecosystem news content into a professional, engaging podcast script for "Arweave Today". 

Date: {date_str}

Raw Content:
{raw_content}

Instructions:
1. Create a natural, conversational flow suitable for audio delivery
2. Use Puck's enthusiastic but professional tone - friendly tech podcaster style
3. Add smooth transitions between topics using phrases like "First up", "Moving on", "Next", "And finally"
4. Explain technical terms in an accessible way for general audiences
5. Maintain excitement about the Arweave ecosystem and permanent web
6. Keep the script between 3-5 minutes when spoken (approximately 450-750 words)
7. End with a warm, professional closing

Voice Guidelines for Puck:
- Conversational and warm, like talking to a friend
- Professional but approachable
- Occasionally uses natural filler words ("you know", "well", "now")
- Explains complex concepts simply
- Shows genuine enthusiasm for decentralized technology

Format the output as a clean script without stage directions, music cues, or formatting markers - just the text that should be spoken.'''
    
    def generate_audio(self, script_text: str, output_path: str) -> bool:
        """
        Generate podcast audio using Gemini TTS.
        
        Args:
            script_text: Text to convert to audio
            output_path: Path to save the audio file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print("🎤 Generating podcast audio with Gemini TTS (Puck voice)...")
            
            if not self.client:
                print("⚠️ Gemini client not initialized")
                return False
            
            model = "gemini-2.5-flash-preview-tts"
            
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=script_text),
                    ],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                temperature=1,
                response_modalities=["audio"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Puck"
                        )
                    ),
                ),
            )

            audio_chunks = []
            for chunk in self.client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue
                
                if (chunk.candidates[0].content.parts[0].inline_data and 
                    chunk.candidates[0].content.parts[0].inline_data.data):
                    inline_data = chunk.candidates[0].content.parts[0].inline_data
                    data_buffer = inline_data.data
                    
                    # Convert to WAV if needed
                    if inline_data.mime_type != "audio/wav":
                        data_buffer = convert_to_wav(inline_data.data, inline_data.mime_type)
                    
                    audio_chunks.append(data_buffer)
            
            if audio_chunks:
                # Combine all audio chunks
                combined_audio = b''.join(audio_chunks)
                
                # Ensure output path has .wav extension for Gemini TTS
                output_path = ensure_wav_extension(output_path)
                
                save_binary_file(output_path, combined_audio)
                print(f"✅ Gemini TTS audio generated: {output_path}")
                return True
            else:
                print("⚠️ No audio data received from Gemini TTS")
                return False
                
        except Exception as e:
            print(f"⚠️ Error generating audio with Gemini TTS: {e}")
            return False


# Factory function for creating Gemini service
def create_gemini_service() -> Optional[GeminiService]:
    """
    Create a Gemini service instance with configuration.
    
    Returns:
        GeminiService instance or None if not configured
    """
    if not config.is_gemini_configured():
        print("⚠️ Gemini API key not configured")
        return None
    
    return GeminiService(config.GEMINI_API_KEY)
