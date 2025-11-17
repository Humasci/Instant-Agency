"""
Phase 4: Real-Time Conversation Agent

Combines avatar, voice, and AI for complete real-time interactions.
This is the "full package" - the ultimate AI sales/support agent.

Components:
- Digital Avatar (visual presence)
- Voice synthesis (natural speech)
- Speech recognition (listen to customers)
- Conversational AI (intelligent responses)
- Emotion detection (adapt to customer mood)

Use Cases:
- Live sales calls with video avatar
- Customer support sessions
- Product demos
- Onboarding sessions
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime
from base_agent import BaseAgent


class Phase4RealTimeConversationAgent(BaseAgent):
    """
    Real-Time Conversation Agent - The Complete Package
    Combines all Phase 4 capabilities for full avatar-led conversations
    """

    def __init__(self):
        super().__init__(
            agent_name="phase4_realtime_conversation",
            agent_type="realtime",
            model_name="combined"
        )

        # Initialize sub-agents (would import in production)
        self.avatar_agent = None  # Phase4DigitalAvatarAgent()
        self.voice_agent = None  # Phase4VoiceConversationAgent()
        self.multilingual_agent = None  # Phase4MultilingualAgent()

        # Active sessions
        self.active_sessions = {}

        print(f"✓ Real-Time Conversation Agent initialized")
        print(f"  Combines: Avatar + Voice + AI + Multilingual")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process real-time conversation session

        Args:
            input_data: {
                'action': 'start_session' | 'process_turn' | 'end_session',
                'session_id': str,
                'persona': str,  # 'sarah', 'marcus', 'priya'
                'input_type': 'audio' | 'text',
                'input_data': str or bytes,
                'language': str (optional),
                'video_enabled': bool (optional)
            }

        Returns:
            Session data with audio/video response
        """
        try:
            action = input_data.get('action', 'start_session')

            if action == 'start_session':
                return self._start_session(input_data)
            elif action == 'process_turn':
                return self._process_turn(input_data)
            elif action == 'end_session':
                return self._end_session(input_data)
            elif action == 'get_session_info':
                return self._get_session_info(input_data)
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            self.logger.error(f"Real-time conversation error: {e}")
            return {'success': False, 'error': str(e)}

    def _start_session(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start new real-time conversation session"""
        import time

        persona = input_data.get('persona', 'sarah')
        video_enabled = input_data.get('video_enabled', True)
        language = input_data.get('language', 'en')

        session_id = f"session_{int(time.time())}_{persona}"

        # Create session
        session = {
            'session_id': session_id,
            'persona': persona,
            'video_enabled': video_enabled,
            'language': language,
            'started_at': datetime.now().isoformat(),
            'turns': 0,
            'conversation_history': [],
            'status': 'active'
        }

        self.active_sessions[session_id] = session

        # Generate greeting
        greetings = {
            'sarah': "Hello! I'm Sarah, your AI sales consultant. I'm excited to learn about your business and show you how we can help. What would you like to discuss today?",
            'marcus': "Hi, I'm Marcus, your technical solutions architect. I'm here to answer any technical questions and help you understand how to implement our AI agents. Where would you like to start?",
            'priya': "Welcome! I'm Priya, your customer success manager. I'm here to ensure you get maximum value from our platform. How can I help you today?"
        }

        greeting = greetings.get(persona, greetings['sarah'])

        # Generate avatar greeting (if video enabled)
        avatar_video_id = None
        if video_enabled:
            # Would call avatar agent here
            avatar_video_id = f"greeting_{session_id}"

        return {
            'success': True,
            'session_id': session_id,
            'persona': persona,
            'greeting_text': greeting,
            'greeting_audio': 'base64_audio_data_here',  # Would be actual TTS output
            'avatar_video_id': avatar_video_id,
            'video_enabled': video_enabled,
            'language': language,
            'websocket_url': f'wss://realtime.instant-agency.ai/session/{session_id}',
            'status': 'active',
            'timestamp': datetime.now().isoformat()
        }

    def _process_turn(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a conversation turn"""
        session_id = input_data.get('session_id')
        input_type = input_data.get('input_type', 'text')
        user_input = input_data.get('input_data')

        if not session_id or session_id not in self.active_sessions:
            return {'success': False, 'error': 'Invalid or expired session'}

        session = self.active_sessions[session_id]

        # Step 1: Convert audio to text (if needed)
        if input_type == 'audio':
            # Would call voice agent for STT
            user_text = "Transcribed user speech here"
        else:
            user_text = user_input

        # Step 2: Detect emotion/intent
        emotion = self._detect_emotion(user_text)
        intent = self._classify_intent(user_text)

        # Step 3: Generate AI response
        ai_response = self._generate_contextual_response(
            user_text,
            session['conversation_history'],
            intent,
            emotion
        )

        # Step 4: Convert response to audio
        audio_response = "base64_audio_response"  # Would be TTS output

        # Step 5: Generate avatar video (if enabled)
        avatar_video_id = None
        if session['video_enabled']:
            avatar_video_id = f"turn_{session['turns']}_{session_id}"

        # Update session
        session['turns'] += 1
        session['conversation_history'].append({
            'turn': session['turns'],
            'user': user_text,
            'ai': ai_response,
            'intent': intent,
            'emotion': emotion,
            'timestamp': datetime.now().isoformat()
        })

        return {
            'success': True,
            'session_id': session_id,
            'turn_number': session['turns'],
            'user_input': user_text,
            'ai_response': ai_response,
            'audio_response': audio_response,
            'avatar_video_id': avatar_video_id,
            'detected_emotion': emotion,
            'detected_intent': intent,
            'timestamp': datetime.now().isoformat()
        }

    def _end_session(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """End conversation session"""
        session_id = input_data.get('session_id')

        if not session_id or session_id not in self.active_sessions:
            return {'success': False, 'error': 'Session not found'}

        session = self.active_sessions.pop(session_id)
        session['status'] = 'ended'
        session['ended_at'] = datetime.now().isoformat()

        # Calculate session metrics
        total_turns = session['turns']
        duration = session['ended_at']  # Would calculate actual duration

        # Generate session summary
        summary = self._generate_session_summary(session)

        return {
            'success': True,
            'session_id': session_id,
            'total_turns': total_turns,
            'duration': duration,
            'summary': summary,
            'conversation_history': session['conversation_history'],
            'next_steps': summary.get('recommended_actions', []),
            'timestamp': datetime.now().isoformat()
        }

    def _get_session_info(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about active session"""
        session_id = input_data.get('session_id')

        if not session_id or session_id not in self.active_sessions:
            return {'success': False, 'error': 'Session not found'}

        session = self.active_sessions[session_id]

        return {
            'success': True,
            'session_id': session_id,
            'persona': session['persona'],
            'turns': session['turns'],
            'started_at': session['started_at'],
            'status': session['status'],
            'video_enabled': session['video_enabled'],
            'language': session['language']
        }

    def _detect_emotion(self, text: str) -> str:
        """Detect emotion from text (simplified)"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['angry', 'frustrated', 'upset', '!!']):
            return 'frustrated'
        elif any(word in text_lower for word in ['happy', 'great', 'excellent', 'thank you']):
            return 'positive'
        elif any(word in text_lower for word in ['confused', 'unclear', 'don\'t understand']):
            return 'confused'
        else:
            return 'neutral'

    def _classify_intent(self, text: str) -> str:
        """Classify user intent (simplified)"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['price', 'cost', 'pricing']):
            return 'pricing_inquiry'
        elif any(word in text_lower for word in ['demo', 'see', 'show']):
            return 'demo_request'
        elif any(word in text_lower for word in ['how', 'help', 'benefit']):
            return 'information_seeking'
        elif any(word in text_lower for word in ['integrate', 'implementation']):
            return 'technical_inquiry'
        else:
            return 'general'

    def _generate_contextual_response(
        self,
        user_text: str,
        history: List,
        intent: str,
        emotion: str
    ) -> str:
        """Generate contextual AI response"""
        # Adapt response based on emotion
        if emotion == 'frustrated':
            prefix = "I understand your frustration, and I'm here to help. "
        elif emotion == 'confused':
            prefix = "Let me clarify that for you. "
        elif emotion == 'positive':
            prefix = "I'm glad to hear that! "
        else:
            prefix = ""

        # Generate response based on intent
        responses = {
            'pricing_inquiry': "Our pricing is flexible and based on your specific needs. We offer plans from $999/month for small businesses up to custom enterprise solutions. Most importantly, our clients typically see ROI within 3-6 months. Would you like me to walk you through our pricing tiers?",
            'demo_request': "Absolutely! I'd love to give you a personalized demo. We can schedule a 30-minute session where I'll show you exactly how our AI agents work with your specific use case. What's your availability this week?",
            'technical_inquiry': "Great question! Our platform integrates seamlessly with most popular tools through our REST API and pre-built connectors. We support Salesforce, HubSpot, Slack, and many others. What systems are you currently using?",
            'information_seeking': "I'd be happy to explain! Our AI agents automate time-consuming tasks like lead qualification, customer support, and content creation - freeing your team to focus on strategic work. They're available 24/7 and provide consistent, high-quality interactions. What specific challenge are you looking to solve?",
            'general': "Thank you for sharing that. I want to make sure I understand your needs correctly. Could you tell me a bit more about what you're hoping to achieve?"
        }

        response = responses.get(intent, responses['general'])

        return prefix + response

    def _generate_session_summary(self, session: Dict) -> Dict[str, Any]:
        """Generate summary of conversation session"""
        history = session['conversation_history']

        # Extract intents from conversation
        intents_discussed = list(set(turn['intent'] for turn in history))

        # Determine next steps
        recommended_actions = []

        if 'pricing_inquiry' in intents_discussed:
            recommended_actions.append({
                'action': 'send_pricing_proposal',
                'priority': 'high'
            })

        if 'demo_request' in intents_discussed:
            recommended_actions.append({
                'action': 'schedule_demo',
                'priority': 'critical'
            })

        if 'technical_inquiry' in intents_discussed:
            recommended_actions.append({
                'action': 'technical_consultation',
                'priority': 'medium'
            })

        return {
            'total_turns': len(history),
            'intents_discussed': intents_discussed,
            'recommended_actions': recommended_actions,
            'engagement_level': 'high' if len(history) >= 5 else 'medium' if len(history) >= 3 else 'low',
            'follow_up_needed': len(recommended_actions) > 0
        }


if __name__ == "__main__":
    print("\n" + "="*80)
    print("Testing Phase 4 Real-Time Conversation Agent")
    print("="*80 + "\n")

    agent = Phase4RealTimeConversationAgent()

    # Test: Full conversation flow
    print("Test: Complete conversation session")
    print("-"*80)

    # Start session
    result = agent.process({
        'action': 'start_session',
        'persona': 'sarah',
        'video_enabled': True
    })

    session_id = result['session_id']
    print(f"✓ Session started: {session_id}")
    print(f"✓ Greeting: {result['greeting_text'][:60]}...")

    # Process turns
    result = agent.process({
        'action': 'process_turn',
        'session_id': session_id,
        'input_type': 'text',
        'input_data': 'What are your pricing options?'
    })

    print(f"\n✓ Turn {result['turn_number']}")
    print(f"  User: What are your pricing options?")
    print(f"  AI: {result['ai_response'][:80]}...")
    print(f"  Intent: {result['detected_intent']}")

    # End session
    result = agent.process({
        'action': 'end_session',
        'session_id': session_id
    })

    print(f"\n✓ Session ended")
    print(f"  Total turns: {result['total_turns']}")
    print(f"  Summary: {result['summary']}")

    print("\n" + "="*80)
    print("Real-Time Conversation Agent Tests Complete!")
    print("="*80)
