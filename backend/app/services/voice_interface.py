# app/services/voice_interface.py
import io
import base64
import asyncio
from fastapi import UploadFile
from typing import Dict, Any, Optional
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os
from pydantic import BaseModel
from datetime import datetime
import json

class VoiceRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    language: str = "en-US"
    response_voice: bool = True
    voice_speed: float = 1.0

class VoiceResponse(BaseModel):
    transcript: str
    response_text: str
    audio_response: Optional[str] = None  # Base64 encoded audio response
    confidence: float
    processing_time_ms: int
    timestamp: str

class VoiceInterfaceService:
    """
    Voice Interface Service for Maritime AI Agent
    Handles speech-to-text, text-to-speech, and voice commands
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.supported_languages = {
            "en-US": "English (US)",
            "en-GB": "English (UK)", 
            "es-ES": "Spanish",
            "fr-FR": "French",
            "de-DE": "German",
            "it-IT": "Italian",
            "pt-BR": "Portuguese (Brazil)",
            "zh-CN": "Chinese (Mandarin)",
            "ja-JP": "Japanese",
            "ko-KR": "Korean"
        }
        
        # Voice command shortcuts for maritime operations
        self.voice_shortcuts = {
            "weather check": "Get weather forecast for current location",
            "route plan": "Plan optimal route between two ports",
            "fuel optimize": "Calculate fuel optimization recommendations", 
            "risk analysis": "Analyze risks along planned route",
            "piracy zones": "Show current piracy risk zones",
            "port info": "Get information about major ports",
            "emergency": "Activate emergency protocols and information"
        }

    async def process_voice_input(self, audio_file: UploadFile, 
                                language: str = "en-US",
                                response_voice: bool = True) -> VoiceResponse:
        """
        Process voice input and return voice response
        
        Args:
            audio_file: Audio file upload (WAV, MP3, etc.)
            language: Language code for speech recognition
            response_voice: Whether to generate audio response
        """
        start_time = datetime.now()
        
        try:
            # Read audio file
            audio_data = await audio_file.read()
            
            # Convert to speech
            transcript = await self._speech_to_text(audio_data, language)
            
            if not transcript:
                return VoiceResponse(
                    transcript="",
                    response_text="Sorry, I couldn't understand the audio. Please try again.",
                    confidence=0.0,
                    processing_time_ms=self._get_processing_time(start_time),
                    timestamp=datetime.now().isoformat()
                )
            
            # Process command (integrate with existing maritime agent)
            response_text = await self._process_maritime_command(transcript)
            
            # Generate voice response if requested
            audio_response = None
            if response_voice:
                audio_response = await self._text_to_speech(response_text, language)
            
            processing_time = self._get_processing_time(start_time)
            
            return VoiceResponse(
                transcript=transcript,
                response_text=response_text,
                audio_response=audio_response,
                confidence=0.95,  # Placeholder - would use actual confidence from speech recognition
                processing_time_ms=processing_time,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return VoiceResponse(
                transcript="",
                response_text=f"Voice processing error: {str(e)}",
                confidence=0.0,
                processing_time_ms=self._get_processing_time(start_time),
                timestamp=datetime.now().isoformat()
            )

    async def _speech_to_text(self, audio_data: bytes, language: str) -> str:
        """Convert speech to text using speech recognition"""
        try:
            # Create temporary file for audio processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name
            
            # Load audio file
            with sr.AudioFile(temp_audio_path) as source:
                audio = self.recognizer.record(source)
            
            # Recognize speech
            try:
                # Try Google Web Speech API first
                transcript = self.recognizer.recognize_google(audio, language=language)
            except sr.RequestError:
                # Fallback to offline recognition
                transcript = self.recognizer.recognize_sphinx(audio)
            except sr.UnknownValueError:
                transcript = ""
            
            # Clean up temporary file
            os.unlink(temp_audio_path)
            
            return transcript.strip()
            
        except Exception as e:
            print(f"Speech recognition error: {e}")
            return ""

    async def _text_to_speech(self, text: str, language: str) -> str:
        """Convert text to speech and return base64 encoded audio"""
        try:
            # Map language codes for gTTS
            tts_lang = language.split('-')[0]  # e.g., 'en-US' -> 'en'
            
            # Generate speech
            tts = gTTS(text=text, lang=tts_lang, slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                tts.save(temp_audio.name)
                temp_audio_path = temp_audio.name
            
            # Read audio file and encode to base64
            with open(temp_audio_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            # Clean up temporary file
            os.unlink(temp_audio_path)
            
            return audio_base64
            
        except Exception as e:
            print(f"Text-to-speech error: {e}")
            return None

    async def _process_maritime_command(self, transcript: str) -> str:
        """
        Process maritime voice command and generate response
        This would integrate with your existing maritime agent
        """
        transcript_lower = transcript.lower()
        
        # Check for voice shortcuts
        for shortcut, description in self.voice_shortcuts.items():
            if shortcut in transcript_lower:
                return await self._handle_voice_shortcut(shortcut, transcript)
        
        # Check for specific maritime operations
        if any(word in transcript_lower for word in ["weather", "forecast", "temperature"]):
            return await self._handle_weather_command(transcript)
        
        elif any(word in transcript_lower for word in ["route", "plan", "navigate", "voyage"]):
            return await self._handle_route_command(transcript)
        
        elif any(word in transcript_lower for word in ["fuel", "consumption", "optimize"]):
            return await self._handle_fuel_command(transcript)
        
        elif any(word in transcript_lower for word in ["risk", "danger", "piracy", "safety"]):
            return await self._handle_risk_command(transcript)
        
        elif any(word in transcript_lower for word in ["port", "harbor", "terminal"]):
            return await self._handle_port_command(transcript)
        
        elif any(word in transcript_lower for word in ["emergency", "mayday", "distress"]):
            return await self._handle_emergency_command(transcript)
        
        else:
            # General maritime query - pass to main agent
            return f"I heard: '{transcript}'. Let me process this maritime query for you. This would integrate with your main maritime agent to provide a comprehensive response."

    async def _handle_voice_shortcut(self, shortcut: str, full_transcript: str) -> str:
        """Handle predefined voice shortcuts"""
        responses = {
            "weather check": "Checking weather conditions for your current area. I'll need your coordinates or location name to provide accurate weather data.",
            "route plan": "I'm ready to plan your optimal route. Please specify your departure and destination ports.",
            "fuel optimize": "Preparing fuel optimization analysis. What is your vessel type and planned route distance?",
            "risk analysis": "Initiating risk analysis. Please provide your route waypoints for comprehensive assessment.",
            "piracy zones": "Current global piracy risk zones: Gulf of Aden (High Risk), Gulf of Guinea (High Risk), Strait of Malacca (Medium Risk). Would you like detailed information for a specific area?",
            "port info": "Port information system ready. Which port would you like information about?",
            "emergency": "Emergency protocols activated. For immediate assistance, contact relevant maritime authorities. How can I help with your emergency situation?"
        }
        
        return responses.get(shortcut, "Voice shortcut recognized. Processing your request.")

    async def _handle_weather_command(self, transcript: str) -> str:
        """Handle weather-related voice commands"""
        # Extract location if mentioned
        words = transcript.lower().split()
        location_indicators = ["for", "at", "in", "near", "around"]
        
        location = None
        for i, word in enumerate(words):
            if word in location_indicators and i + 1 < len(words):
                location = " ".join(words[i+1:])
                break
        
        if location:
            return f"Getting weather forecast for {location}. Current conditions and 48-hour forecast will be provided."
        else:
            return "I can provide weather information. Please specify your location or coordinates."

    async def _handle_route_command(self, transcript: str) -> str:
        """Handle route planning voice commands"""
        # Try to extract origin and destination
        words = transcript.lower().split()
        
        # Look for common route patterns
        if "from" in words and "to" in words:
            from_idx = words.index("from")
            to_idx = words.index("to")
            
            if from_idx < to_idx:
                origin = " ".join(words[from_idx+1:to_idx])
                destination = " ".join(words[to_idx+1:])
                return f"Planning optimal route from {origin} to {destination}. Analyzing weather, piracy risks, fuel costs, and efficiency factors."
        
        return "I can help plan your voyage route. Please specify your departure and destination ports."

    async def _handle_fuel_command(self, transcript: str) -> str:
        """Handle fuel optimization voice commands"""
        return "Fuel optimization analysis ready. I'll calculate optimal speed and consumption based on your vessel type, route distance, and current weather conditions."

    async def _handle_risk_command(self, transcript: str) -> str:
        """Handle risk analysis voice commands"""
        return "Risk analysis initiated. I'll assess weather hazards, piracy threats, port congestion, and geopolitical risks along your planned route."

    async def _handle_port_command(self, transcript: str) -> str:
        """Handle port information voice commands"""
        return "Port information system active. I have data on major world ports including coordinates, facilities, and regional information."

    async def _handle_emergency_command(self, transcript: str) -> str:
        """Handle emergency voice commands"""
        return "Emergency assistance mode activated. For immediate help, contact Coast Guard or maritime authorities on VHF Channel 16. I can provide navigation assistance, weather updates, and emergency procedures."

    def _get_processing_time(self, start_time: datetime) -> int:
        """Calculate processing time in milliseconds"""
        end_time = datetime.now()
        delta = end_time - start_time
        return int(delta.total_seconds() * 1000)

    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.supported_languages

    def get_voice_shortcuts(self) -> Dict[str, str]:
        """Get list of available voice shortcuts"""
        return self.voice_shortcuts

    async def process_text_with_voice_response(self, text: str, language: str = "en-US") -> Dict[str, Any]:
        """Process text input and return voice response"""
        try:
            # Process the text command
            response_text = await self._process_maritime_command(text)
            
            # Generate voice response
            audio_response = await self._text_to_speech(response_text, language)
            
            return {
                "input_text": text,
                "response_text": response_text,
                "audio_response": audio_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "input_text": text,
                "response_text": f"Error processing text: {str(e)}",
                "audio_response": None,
                "timestamp": datetime.now().isoformat()
            }

    def get_service_status(self) -> Dict[str, Any]:
        """Get voice interface service status"""
        return {
            "service": "Voice Interface",
            "status": "operational",
            "capabilities": {
                "speech_to_text": True,
                "text_to_speech": True,
                "voice_shortcuts": len(self.voice_shortcuts),
                "supported_languages": len(self.supported_languages)
            },
            "features": [
                "Multi-language support",
                "Voice command shortcuts",
                "Maritime-specific commands",
                "Emergency voice protocols",
                "Audio response generation"
            ],
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat()
        }