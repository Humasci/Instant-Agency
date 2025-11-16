"""
Phase 4: Voice-Enabled Conversation Agent

Handles voice-to-voice conversations with AI agents using:
- Speech-to-Text (STT): Wav2Vec2
- Conversational AI: GPT-Neo/Mistral
- Text-to-Speech (TTS): Multiple providers

Key Features:
- Real-time voice transcription
- Natural voice synthesis
- Conversation context management
- Emotion and tone control
- Multi-language support
- Interrupt handling

Models:
- STT: facebook/wav2vec2-large-960h-lv60-self
- TTS: ElevenLabs, Microsoft Azure, Google Cloud
"""

import os
import json
import time
import requests
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from base_agent import BaseAgent


class TTSProvider(Enum):
    """Text-to-Speech providers"""
    ELEVENLABS = "elevenlabs"
    AZURE = "azure"
    GOOGLE = "google"
    SIMULATED = "simulated"


class Phase4VoiceConversationAgent(BaseAgent):
    """
    Voice-Enabled Conversation Agent for voice-to-voice interactions
    """

    def __init__(self):
        super().__init__(
            agent_name="phase4_voice_conversation",
            agent_type="voice",
            model_name="facebook/wav2vec2-large-960h-lv60-self"
        )

        # STT Model (Wav2Vec2)
        self.stt_model = "facebook/wav2vec2-large-960h-lv60-self"

        # TTS Configuration
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        self.azure_speech_key = os.getenv('AZURE_SPEECH_KEY')
        self.azure_speech_region = os.getenv('AZURE_SPEECH_REGION', 'eastus')

        # Determine TTS provider
        if self.elevenlabs_api_key:
            self.tts_provider = TTSProvider.ELEVENLABS
        elif self.azure_speech_key:
            self.tts_provider = TTSProvider.AZURE
        else:
            self.tts_provider = TTSProvider.SIMULATED
            print("⚠️  No TTS API keys found - using simulated mode")

        # Conversation context
        self.active_conversations = {}

        # Voice configurations
        self.voices = {
            'sarah': {
                'elevenlabs_voice_id': '21m00Tcm4TlvDq8ikWAM',  # Rachel
                'azure_voice': 'en-US-JennyNeural',
                'google_voice': 'en-US-Wavenet-F',
                'style': 'friendly, professional',
                'speaking_rate': 1.0
            },
            'marcus': {
                'elevenlabs_voice_id': 'VR6AewLTigWG4xSOukaG',  # Arnold
                'azure_voice': 'en-US-GuyNeural',
                'google_voice': 'en-US-Wavenet-D',
                'style': 'authoritative, clear',
                'speaking_rate': 0.95
            },
            'priya': {
                'elevenlabs_voice_id': 'EXAVITQu4vr4xnSDxMaL',  # Bella
                'azure_voice': 'en-US-AriaNeural',
                'google_voice': 'en-US-Wavenet-C',
                'style': 'warm, supportive',
                'speaking_rate': 1.05
            }
        }

        print(f"✓ Voice Conversation Agent initialized")
        print(f"  STT Model: {self.stt_model}")
        print(f"  TTS Provider: {self.tts_provider.value}")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process voice interaction

        Args:
            input_data: {
                'action': str,  # 'transcribe', 'synthesize', 'conversation_turn'
                'audio_data': str (base64) or bytes,  # For transcription
                'text': str,  # For synthesis
                'voice': str,  # 'sarah', 'marcus', 'priya'
                'conversation_id': str (optional),
                'language': str (optional),
                'emotion': str (optional)  # 'happy', 'serious', 'empathetic'
            }

        Returns:
            Transcription or audio data
        """
        try:
            action = input_data.get('action', 'conversation_turn')

            if action == 'transcribe':
                return self._transcribe_audio(input_data)
            elif action == 'synthesize':
                return self._synthesize_speech(input_data)
            elif action == 'conversation_turn':
                return self._handle_conversation_turn(input_data)
            elif action == 'start_conversation':
                return self._start_conversation(input_data)
            elif action == 'end_conversation':
                return self._end_conversation(input_data)
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            self.logger.error(f"Voice conversation error: {e}")
            return {'success': False, 'error': str(e)}

    def _transcribe_audio(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transcribe audio to text using Wav2Vec2"""
        audio_data = input_data.get('audio_data')

        if not audio_data:
            return {'success': False, 'error': 'No audio data provided'}

        # In production, call Hugging Face Inference API
        # For now, simulate transcription
        if self.hf_api_key:
            try:
                # Decode base64 if needed
                if isinstance(audio_data, str):
                    audio_bytes = base64.b64decode(audio_data)
                else:
                    audio_bytes = audio_data

                url = f"{self.hf_api_url}/{self.stt_model}"
                headers = {"Authorization": f"Bearer {self.hf_api_key}"}

                response = requests.post(
                    url,
                    headers=headers,
                    data=audio_bytes,
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    transcription = result.get('text', '')

                    return {
                        'success': True,
                        'transcription': transcription,
                        'confidence': result.get('confidence', 0.9),
                        'language': 'en',
                        'model': self.stt_model
                    }
                else:
                    return {
                        'success': False,
                        'error': f'STT API error: {response.status_code}'
                    }

            except Exception as e:
                return {'success': False, 'error': f'STT failed: {str(e)}'}
        else:
            # Simulated transcription
            return {
                'success': True,
                'transcription': 'Hello, I would like to learn more about your AI agents and how they can help my business.',
                'confidence': 0.95,
                'language': 'en',
                'model': 'simulated',
                'note': 'Configure HUGGINGFACE_API_KEY for real transcription'
            }

    def _synthesize_speech(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert text to speech"""
        text = input_data.get('text')
        voice = input_data.get('voice', 'sarah')

        if not text:
            return {'success': False, 'error': 'No text provided'}

        voice_config = self.voices.get(voice, self.voices['sarah'])

        # Synthesize based on provider
        if self.tts_provider == TTSProvider.ELEVENLABS:
            return self._synthesize_elevenlabs(text, voice_config, input_data)
        elif self.tts_provider == TTSProvider.AZURE:
            return self._synthesize_azure(text, voice_config, input_data)
        else:
            return self._synthesize_simulated(text, voice_config, input_data)

    def _synthesize_elevenlabs(
        self,
        text: str,
        voice_config: Dict,
        options: Dict
    ) -> Dict[str, Any]:
        """Synthesize using ElevenLabs"""
        if not self.elevenlabs_api_key:
            return {'success': False, 'error': 'ElevenLabs API key not configured'}

        voice_id = voice_config['elevenlabs_voice_id']
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "xi-api-key": self.elevenlabs_api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                audio_base64 = base64.b64encode(response.content).decode('utf-8')

                return {
                    'success': True,
                    'audio_data': audio_base64,
                    'format': 'mp3',
                    'provider': 'elevenlabs',
                    'voice': voice_config['style'],
                    'text_length': len(text),
                    'estimated_duration': len(text.split()) / 150 * 60  # ~150 WPM
                }
            else:
                return {
                    'success': False,
                    'error': f'ElevenLabs API error: {response.status_code}'
                }

        except Exception as e:
            return {'success': False, 'error': f'TTS failed: {str(e)}'}

    def _synthesize_azure(
        self,
        text: str,
        voice_config: Dict,
        options: Dict
    ) -> Dict[str, Any]:
        """Synthesize using Azure Speech"""
        if not self.azure_speech_key:
            return {'success': False, 'error': 'Azure Speech key not configured'}

        url = f"https://{self.azure_speech_region}.tts.speech.microsoft.com/cognitiveservices/v1"

        headers = {
            "Ocp-Apim-Subscription-Key": self.azure_speech_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3"
        }

        # SSML for better control
        ssml = f"""
        <speak version='1.0' xml:lang='en-US'>
            <voice name='{voice_config["azure_voice"]}'>
                <prosody rate='{voice_config["speaking_rate"]}'>
                    {text}
                </prosody>
            </voice>
        </speak>
        """

        try:
            response = requests.post(url, headers=headers, data=ssml, timeout=30)

            if response.status_code == 200:
                audio_base64 = base64.b64encode(response.content).decode('utf-8')

                return {
                    'success': True,
                    'audio_data': audio_base64,
                    'format': 'mp3',
                    'provider': 'azure',
                    'voice': voice_config['azure_voice'],
                    'text_length': len(text),
                    'estimated_duration': len(text.split()) / 150 * 60
                }
            else:
                return {
                    'success': False,
                    'error': f'Azure TTS error: {response.status_code}'
                }

        except Exception as e:
            return {'success': False, 'error': f'Azure TTS failed: {str(e)}'}

    def _synthesize_simulated(
        self,
        text: str,
        voice_config: Dict,
        options: Dict
    ) -> Dict[str, Any]:
        """Simulate TTS for testing"""
        # Create fake audio data (base64 encoded placeholder)
        fake_audio = base64.b64encode(b"SIMULATED_AUDIO_DATA").decode('utf-8')

        return {
            'success': True,
            'audio_data': fake_audio,
            'format': 'mp3',
            'provider': 'simulated',
            'voice': voice_config['style'],
            'text_length': len(text),
            'estimated_duration': len(text.split()) / 150 * 60,
            'note': 'Configure ELEVENLABS_API_KEY or AZURE_SPEECH_KEY for real TTS'
        }

    def _handle_conversation_turn(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle complete conversation turn (STT → LLM → TTS)"""
        conversation_id = input_data.get('conversation_id')
        audio_data = input_data.get('audio_data')
        text_input = input_data.get('text')  # Alternative to audio
        voice = input_data.get('voice', 'sarah')

        # Step 1: Transcribe audio (if provided)
        if audio_data:
            stt_result = self._transcribe_audio({'audio_data': audio_data})
            if not stt_result.get('success'):
                return stt_result
            user_text = stt_result['transcription']
        elif text_input:
            user_text = text_input
        else:
            return {'success': False, 'error': 'No audio or text input provided'}

        # Step 2: Get conversation context
        context = self.active_conversations.get(conversation_id, {
            'history': [],
            'voice': voice,
            'started_at': datetime.now().isoformat()
        })

        # Add user message to history
        context['history'].append({
            'role': 'user',
            'content': user_text,
            'timestamp': datetime.now().isoformat()
        })

        # Step 3: Generate AI response (simulated - in production use LLM)
        ai_response = self._generate_response(user_text, context)

        # Add AI response to history
        context['history'].append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now().isoformat()
        })

        # Update conversation
        self.active_conversations[conversation_id] = context

        # Step 4: Synthesize response to audio
        tts_result = self._synthesize_speech({
            'text': ai_response,
            'voice': voice
        })

        if not tts_result.get('success'):
            return tts_result

        # Return complete turn
        return {
            'success': True,
            'conversation_id': conversation_id,
            'user_input': user_text,
            'ai_response': ai_response,
            'audio_response': tts_result['audio_data'],
            'audio_format': tts_result['format'],
            'turn_count': len(context['history']) // 2,
            'timestamp': datetime.now().isoformat()
        }

    def _generate_response(self, user_text: str, context: Dict) -> str:
        """Generate AI response (simplified - in production use LLM)"""
        # In production, this would call phase2_sales_pitch or phase3_sales_strategist
        # For now, use template-based responses

        user_lower = user_text.lower()

        if 'pricing' in user_lower or 'cost' in user_lower or 'price' in user_lower:
            return "Great question! Our AI agents are priced based on your needs. We offer flexible plans starting at $999/month for small businesses, with enterprise options available. The best part? Most clients see ROI within 3-6 months through automation savings. Would you like me to walk you through our pricing tiers?"

        elif 'demo' in user_lower or 'see it' in user_lower or 'show me' in user_lower:
            return "Absolutely! I'd love to show you our AI agents in action. We can schedule a personalized demo where I'll demonstrate how our agents can specifically help your business. What's your availability like this week?"

        elif 'help' in user_lower or 'benefits' in user_lower or 'how' in user_lower:
            return "Our AI agents can transform your business in several ways: First, they automate repetitive tasks like lead qualification and customer support, freeing up your team for strategic work. Second, they provide 24/7 availability without breaks. Third, they ensure consistent, high-quality interactions every time. What specific challenge are you looking to solve?"

        elif 'integrate' in user_lower or 'integration' in user_lower:
            return "Integration is seamless! Our agents work with popular tools like Salesforce, HubSpot, Slack, and more through our API. We also offer pre-built connectors for common workflows. The typical integration takes 1-2 weeks. What systems are you currently using?"

        else:
            return "Thank you for that question. I want to make sure I understand your needs correctly so I can provide the most helpful information. Could you tell me a bit more about what you're looking to achieve with AI automation?"

    def _start_conversation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new conversation"""
        voice = input_data.get('voice', 'sarah')
        conversation_id = f"conv_{int(time.time())}_{voice}"

        self.active_conversations[conversation_id] = {
            'history': [],
            'voice': voice,
            'started_at': datetime.now().isoformat(),
            'turns': 0
        }

        # Generate greeting
        greeting = self._get_greeting(voice)

        # Synthesize greeting
        tts_result = self._synthesize_speech({
            'text': greeting,
            'voice': voice
        })

        return {
            'success': True,
            'conversation_id': conversation_id,
            'greeting_text': greeting,
            'greeting_audio': tts_result.get('audio_data'),
            'voice': voice,
            'timestamp': datetime.now().isoformat()
        }

    def _end_conversation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """End conversation and get summary"""
        conversation_id = input_data.get('conversation_id')

        if conversation_id not in self.active_conversations:
            return {'success': False, 'error': 'Conversation not found'}

        context = self.active_conversations.pop(conversation_id)

        return {
            'success': True,
            'conversation_id': conversation_id,
            'total_turns': len(context['history']) // 2,
            'duration': context['started_at'],
            'summary': f"Conversation with {context['voice']} - {len(context['history']) // 2} exchanges",
            'conversation_history': context['history']
        }

    def _get_greeting(self, voice: str) -> str:
        """Get personalized greeting based on voice/persona"""
        greetings = {
            'sarah': "Hello! I'm Sarah Williams, your AI sales consultant. I'm here to help you discover how our AI agents can transform your business. What brings you here today?",
            'marcus': "Hi there, I'm Marcus Chen, technical solutions architect. I specialize in helping businesses implement AI automation. What would you like to learn about?",
            'priya': "Welcome! I'm Priya Patel, your customer success manager. I'm excited to help you get the most out of our AI platform. How can I assist you today?"
        }

        return greetings.get(voice, greetings['sarah'])


if __name__ == "__main__":
    # Test the voice conversation agent
    print("\n" + "="*80)
    print("Testing Phase 4 Voice Conversation Agent")
    print("="*80 + "\n")

    agent = Phase4VoiceConversationAgent()

    # Test 1: Start conversation
    print("Test 1: Start conversation")
    print("-"*80)
    result = agent.process({
        'action': 'start_conversation',
        'voice': 'sarah'
    })

    if result.get('success'):
        conversation_id = result['conversation_id']
        print(f"✓ Conversation ID: {conversation_id}")
        print(f"✓ Greeting: {result['greeting_text'][:80]}...")
        print(f"✓ Voice: {result['voice']}")

    # Test 2: Conversation turn
    print("\n\nTest 2: Conversation turn (text input)")
    print("-"*80)
    result = agent.process({
        'action': 'conversation_turn',
        'conversation_id': conversation_id,
        'text': 'What are your pricing options?',
        'voice': 'sarah'
    })

    if result.get('success'):
        print(f"✓ User: {result['user_input']}")
        print(f"✓ AI Response: {result['ai_response'][:100]}...")
        print(f"✓ Turn count: {result['turn_count']}")

    # Test 3: Text-to-Speech
    print("\n\nTest 3: Text-to-Speech synthesis")
    print("-"*80)
    result = agent.process({
        'action': 'synthesize',
        'text': 'Our AI agents can help your business grow faster and more efficiently.',
        'voice': 'marcus'
    })

    if result.get('success'):
        print(f"✓ Provider: {result['provider']}")
        print(f"✓ Format: {result['format']}")
        print(f"✓ Duration: {result['estimated_duration']:.1f}s")
        print(f"✓ Voice: {result['voice']}")

    print("\n" + "="*80)
    print("Voice Conversation Agent Tests Complete!")
    print("="*80)
