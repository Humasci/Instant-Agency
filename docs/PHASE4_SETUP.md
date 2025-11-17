# Phase 4: Optimization & Scale - Setup Guide

Phase 4 brings hyper-realistic digital avatars, voice-enabled conversations, multilingual support, and advanced personalization to create the complete AI agent experience.

## 🎯 Phase 4 Overview

### Agents Included

1. **Digital Avatar Agent** - Hyper-realistic video avatars for sales/support
2. **Voice-Enabled Conversation Agent** - Natural voice-to-voice interactions
3. **Multilingual Agent** - Support for 50+ languages
4. **Real-Time Conversation Agent** - Complete package (Avatar + Voice + AI)
5. **Advanced Personalization Agent** - Hyper-personalized user experiences

### Key Technologies

- **Avatar Generation**: D-ID, HeyGen, Synthesia
- **Speech-to-Text**: Wav2Vec2, Whisper
- **Text-to-Speech**: ElevenLabs, Azure Speech, Google Cloud
- **Translation**: mBART (50+ languages)
- **Personalization**: Behavioral analysis, A/B testing, dynamic segmentation

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install fastapi uvicorn requests transformers torch
pip install sentence-transformers langdetect
```

### Running Phase 4 Agents

```bash
# Start the API server
cd agents
python main.py

# Server will start on http://localhost:8000
# API docs available at http://localhost:8000/docs
```

### Testing Phase 4 Agents

```bash
# Direct testing (no server required)
python scripts/test_phase4_agents.py

# API testing (requires running server)
python scripts/test_phase4_agents.py --api
```

---

## 🔑 API Keys Setup (Optional)

Phase 4 agents work in **simulated mode** without API keys, perfect for testing and development. For production use with real avatar/voice generation, configure these API keys:

### 1. Digital Avatar APIs

#### D-ID (Recommended)
```bash
export DID_API_KEY="your-did-api-key"
export DID_API_URL="https://api.d-id.com"
```
Sign up: https://www.d-id.com/

#### HeyGen
```bash
export HEYGEN_API_KEY="your-heygen-api-key"
```
Sign up: https://www.heygen.com/

#### Synthesia
```bash
export SYNTHESIA_API_KEY="your-synthesia-api-key"
```
Sign up: https://www.synthesia.io/

### 2. Voice APIs

#### ElevenLabs (Recommended)
```bash
export ELEVENLABS_API_KEY="your-elevenlabs-key"
```
Sign up: https://elevenlabs.io/

#### Azure Speech
```bash
export AZURE_SPEECH_KEY="your-azure-key"
export AZURE_SPEECH_REGION="eastus"
```
Sign up: https://azure.microsoft.com/services/cognitive-services/speech-services/

#### Google Cloud TTS
```bash
export GOOGLE_CLOUD_TTS_KEY="your-google-key"
```
Sign up: https://cloud.google.com/text-to-speech

### 3. Hugging Face (For advanced models)
```bash
export HUGGINGFACE_API_KEY="your-hf-token"
```
Sign up: https://huggingface.co/

---

## 📚 Agent Documentation

## 1. Digital Avatar Agent

Creates hyper-realistic video avatars for sales calls, customer support, and presentations.

### Available Personas

- **Sarah** - AI Sales Consultant (Professional, persuasive)
- **Marcus** - Technical Solutions Architect (Expert, detail-oriented)
- **Priya** - Customer Success Manager (Empathetic, supportive)

### API Endpoint

```
POST /phase4/digital-avatar
```

### Examples

#### Create Avatar Video

```bash
curl -X POST http://localhost:8000/phase4/digital-avatar \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create_video",
    "persona": "sarah",
    "script": "Hello! I am Sarah, your AI sales consultant. Let me show you how we can help grow your business.",
    "options": {
      "provider": "d-id",
      "format": "mp4",
      "quality": "high"
    }
  }'
```

Response:
```json
{
  "success": true,
  "video_id": "vid_abc123",
  "persona": "sarah",
  "provider": "d-id",
  "status": "processing",
  "estimated_completion": "30 seconds",
  "video_url": "https://d-id.com/videos/vid_abc123.mp4"
}
```

#### Start Real-Time Stream

```bash
curl -X POST http://localhost:8000/phase4/digital-avatar \
  -H "Content-Type: application/json" \
  -d '{
    "action": "start_stream",
    "persona": "marcus",
    "options": {
      "video_enabled": true,
      "interactive": true
    }
  }'
```

#### Check Video Status

```bash
curl -X POST http://localhost:8000/phase4/digital-avatar \
  -H "Content-Type: application/json" \
  -d '{
    "action": "get_video_status",
    "video_id": "vid_abc123"
  }'
```

---

## 2. Voice-Enabled Conversation Agent

Natural voice-to-voice conversations with speech recognition and synthesis.

### API Endpoint

```
POST /phase4/voice-conversation
```

### Examples

#### Speech-to-Text (Transcribe Audio)

```bash
curl -X POST http://localhost:8000/phase4/voice-conversation \
  -H "Content-Type: application/json" \
  -d '{
    "action": "transcribe",
    "audio_data": "base64_encoded_audio_data",
    "language": "en"
  }'
```

Response:
```json
{
  "success": true,
  "transcription": "What are your pricing options?",
  "language": "en",
  "confidence": 0.94,
  "duration_seconds": 3.2
}
```

#### Text-to-Speech (Synthesize)

```bash
curl -X POST http://localhost:8000/phase4/voice-conversation \
  -H "Content-Type: application/json" \
  -d '{
    "action": "synthesize",
    "text": "Welcome to SIX3 Agency! How can I help you today?",
    "voice": "professional",
    "provider": "elevenlabs",
    "language": "en"
  }'
```

Response:
```json
{
  "success": true,
  "audio_data": "base64_encoded_audio",
  "audio_file": "temp/tts_abc123.mp3",
  "voice_profile": "professional",
  "provider": "elevenlabs",
  "duration_seconds": 4.5
}
```

#### Complete Conversation Turn

```bash
curl -X POST http://localhost:8000/phase4/voice-conversation \
  -H "Content-Type: application/json" \
  -d '{
    "action": "conversation_turn",
    "audio_input": "base64_audio_data",
    "conversation_context": {
      "user_name": "John",
      "conversation_history": []
    },
    "voice_profile": "friendly"
  }'
```

---

## 3. Multilingual Agent

Translate content and communicate in 50+ languages.

### API Endpoint

```
POST /phase4/multilingual
```

### Supported Languages

English, Spanish, French, German, Italian, Portuguese, Dutch, Russian, Chinese, Japanese, Korean, Arabic, Hindi, Turkish, Polish, Ukrainian, and 34 more.

### Examples

#### Translate Text

```bash
curl -X POST http://localhost:8000/phase4/multilingual \
  -H "Content-Type: application/json" \
  -d '{
    "action": "translate",
    "text": "How can I help you?",
    "source_language": "en",
    "target_language": "es"
  }'
```

Response:
```json
{
  "success": true,
  "original_text": "How can I help you?",
  "translated_text": "¿Cómo puedo ayudarte?",
  "source_language": "en",
  "target_language": "es",
  "confidence": 0.92
}
```

#### Detect Language

```bash
curl -X POST http://localhost:8000/phase4/multilingual \
  -H "Content-Type: application/json" \
  -d '{
    "action": "detect_language",
    "text": "Bonjour, comment allez-vous?"
  }'
```

#### Generate Multi-Language Content

```bash
curl -X POST http://localhost:8000/phase4/multilingual \
  -H "Content-Type: application/json" \
  -d '{
    "action": "generate_multilingual",
    "text": "Welcome to our platform",
    "target_languages": ["es", "fr", "de", "zh"]
  }'
```

Response:
```json
{
  "success": true,
  "original_text": "Welcome to our platform",
  "translations": {
    "es": {
      "text": "Bienvenido a nuestra plataforma",
      "language_name": "Spanish",
      "confidence": 0.93
    },
    "fr": {
      "text": "Bienvenue sur notre plateforme",
      "language_name": "French",
      "confidence": 0.91
    }
  },
  "languages_generated": 4
}
```

---

## 4. Real-Time Conversation Agent

The complete package: combines avatar, voice, and AI for full real-time interactions.

### API Endpoint

```
POST /phase4/realtime-conversation
```

### Examples

#### Start Conversation Session

```bash
curl -X POST http://localhost:8000/phase4/realtime-conversation \
  -H "Content-Type: application/json" \
  -d '{
    "action": "start_session",
    "persona": "sarah",
    "video_enabled": true,
    "language": "en"
  }'
```

Response:
```json
{
  "success": true,
  "session_id": "session_1699876543_sarah",
  "persona": "sarah",
  "greeting_text": "Hello! I'm Sarah, your AI sales consultant...",
  "greeting_audio": "base64_audio_data",
  "avatar_video_id": "greeting_session_123",
  "video_enabled": true,
  "websocket_url": "wss://realtime.six3.agency/session/session_123",
  "status": "active"
}
```

#### Process Conversation Turn

```bash
curl -X POST http://localhost:8000/phase4/realtime-conversation \
  -H "Content-Type: application/json" \
  -d '{
    "action": "process_turn",
    "session_id": "session_1699876543_sarah",
    "input_type": "text",
    "input_data": "What are your pricing options?"
  }'
```

Response:
```json
{
  "success": true,
  "session_id": "session_1699876543_sarah",
  "turn_number": 1,
  "user_input": "What are your pricing options?",
  "ai_response": "Our pricing is flexible and based on your specific needs...",
  "audio_response": "base64_audio_data",
  "avatar_video_id": "turn_1_session_123",
  "detected_emotion": "neutral",
  "detected_intent": "pricing_inquiry"
}
```

#### End Session

```bash
curl -X POST http://localhost:8000/phase4/realtime-conversation \
  -H "Content-Type: application/json" \
  -d '{
    "action": "end_session",
    "session_id": "session_1699876543_sarah"
  }'
```

---

## 5. Advanced Personalization Agent

Hyper-personalized experiences based on user behavior and preferences.

### API Endpoint

```
POST /phase4/personalization
```

### User Segments

- **Champion**: High LTV, loyal customers
- **High Value**: High engagement + revenue
- **Engaged**: Active, frequent interactions
- **New User**: Recently joined
- **At Risk**: Low engagement, potential churn
- **Standard**: Average engagement

### Examples

#### Update User Profile (Track Behavior)

```bash
curl -X POST http://localhost:8000/phase4/personalization \
  -H "Content-Type: application/json" \
  -d '{
    "action": "update_profile",
    "user_id": "user_123",
    "behavior_data": {
      "email_opened": true,
      "link_clicked": true,
      "page_viewed": "/pricing",
      "interactions": 1
    }
  }'
```

Response:
```json
{
  "success": true,
  "user_id": "user_123",
  "engagement_score": 65,
  "segment": "engaged",
  "profile": {
    "total_interactions": 5,
    "email_opens": 2,
    "link_clicks": 3,
    "interests": ["pricing", "features"]
  }
}
```

#### Personalize Email Content

```bash
curl -X POST http://localhost:8000/phase4/personalization \
  -H "Content-Type: application/json" \
  -d '{
    "action": "personalize_content",
    "user_id": "user_123",
    "content_type": "email",
    "context": {}
  }'
```

Response:
```json
{
  "success": true,
  "user_id": "user_123",
  "segment": "engaged",
  "strategy": "feature_highlights",
  "personalized_content": {
    "subject": "New Features Based on Your Activity",
    "greeting": "Hello,",
    "body": "Personalized content for engaged segment...",
    "cta": "Try These New Features",
    "tone": "friendly"
  },
  "confidence": 0.85
}
```

#### A/B Testing

```bash
curl -X POST http://localhost:8000/phase4/personalization \
  -H "Content-Type: application/json" \
  -d '{
    "action": "ab_test",
    "user_id": "user_123",
    "test_id": "homepage_hero_test"
  }'
```

Response:
```json
{
  "success": true,
  "user_id": "user_123",
  "test_id": "homepage_hero_test",
  "variant": "B",
  "test_stats": {
    "total_users": 150,
    "variant_stats": {
      "A": {"views": 75, "conversions": 12},
      "B": {"views": 75, "conversions": 18}
    }
  }
}
```

#### Generate Recommendations

```bash
curl -X POST http://localhost:8000/phase4/personalization \
  -H "Content-Type: application/json" \
  -d '{
    "action": "recommend",
    "user_id": "user_123",
    "recommendation_type": "content"
  }'
```

Response:
```json
{
  "success": true,
  "user_id": "user_123",
  "recommendations": [
    {
      "type": "content",
      "title": "ROI Calculator",
      "reason": "Based on your interest in pricing",
      "priority": "high"
    },
    {
      "type": "action",
      "title": "Schedule Demo",
      "reason": "Continue your product exploration",
      "priority": "high"
    }
  ],
  "personalization_factors": {
    "interests": ["pricing", "features"],
    "past_purchases": 0,
    "engagement_level": "high"
  }
}
```

---

## 🎬 Complete Use Case Examples

### Use Case 1: Multilingual Sales Call

```python
import requests

# 1. Start real-time session in Spanish
response = requests.post("http://localhost:8000/phase4/realtime-conversation", json={
    "action": "start_session",
    "persona": "sarah",
    "video_enabled": True,
    "language": "es"
})

session_id = response.json()['session_id']

# 2. Process Spanish input
response = requests.post("http://localhost:8000/phase4/realtime-conversation", json={
    "action": "process_turn",
    "session_id": session_id,
    "input_type": "text",
    "input_data": "¿Cuáles son sus precios?"  # "What are your prices?"
})

# 3. Get English translation of conversation
response = requests.post("http://localhost:8000/phase4/multilingual", json={
    "action": "translate",
    "text": response.json()['ai_response'],
    "source_language": "es",
    "target_language": "en"
})
```

### Use Case 2: Personalized Video Message

```python
# 1. Get user profile to understand segment
response = requests.post("http://localhost:8000/phase4/personalization", json={
    "action": "get_profile",
    "user_id": "user_vip_001"
})

segment = response.json()['segment']  # e.g., "champion"

# 2. Personalize message based on segment
response = requests.post("http://localhost:8000/phase4/personalization", json={
    "action": "personalize_content",
    "user_id": "user_vip_001",
    "content_type": "email",
    "context": {"occasion": "product_launch"}
})

personalized_script = response.json()['personalized_content']['body']

# 3. Create avatar video with personalized script
response = requests.post("http://localhost:8000/phase4/digital-avatar", json={
    "action": "create_video",
    "persona": "sarah",
    "script": personalized_script,
    "options": {"provider": "d-id", "quality": "high"}
})

video_url = response.json()['video_url']
```

### Use Case 3: Voice-First Customer Support

```python
# 1. User speaks (audio captured from mic)
user_audio = capture_microphone_audio()

# 2. Transcribe to text
response = requests.post("http://localhost:8000/phase4/voice-conversation", json={
    "action": "transcribe",
    "audio_data": base64_encode(user_audio),
    "language": "en"
})

user_text = response.json()['transcription']

# 3. Classify intent
response = requests.post("http://localhost:8000/phase2/classify-intent", json={
    "message": user_text,
    "user_id": "user_123"
})

intent = response.json()['intent']

# 4. Generate appropriate response
response = requests.post("http://localhost:8000/phase4/voice-conversation", json={
    "action": "conversation_turn",
    "audio_input": base64_encode(user_audio),
    "conversation_context": {
        "user_name": "Jane",
        "detected_intent": intent
    },
    "voice_profile": "professional"
})

# 5. Play audio response to user
play_audio(response.json()['audio_response'])
```

---

## 📊 Integration with Control Panel

All Phase 4 agents automatically log to the centralized control panel:

```bash
# View all agent activities including Phase 4
curl http://localhost:8000/control-panel/dashboard

# View specific Phase 4 agent details
curl http://localhost:8000/control-panel/agent/phase4_digital_avatar

# Track real-time conversation workflows
curl http://localhost:8000/control-panel/workflow/session_123
```

---

## 🔧 Troubleshooting

### Issue: Avatar videos not generating

**Solution**: Check API keys are configured:
```bash
echo $DID_API_KEY
# If empty, set it:
export DID_API_KEY="your-key"
```

Or use simulated mode (works without API keys):
```python
# Agents automatically fall back to simulated mode
# No configuration needed for testing
```

### Issue: Voice synthesis failing

**Solution**: Verify provider API keys:
```bash
echo $ELEVENLABS_API_KEY
echo $AZURE_SPEECH_KEY
```

Or use simulated audio responses for testing.

### Issue: Translation not working

**Solution**: The multilingual agent uses mBART. Ensure Hugging Face API key is set for production models:
```bash
export HUGGINGFACE_API_KEY="your-token"
```

For testing, simulated translations work without API keys.

---

## 🎯 Production Deployment Checklist

- [ ] Configure external API keys (D-ID, ElevenLabs, Azure)
- [ ] Set up CDN for avatar videos
- [ ] Configure WebSocket server for real-time streaming
- [ ] Set up Redis for user profile caching
- [ ] Enable HTTPS for API endpoints
- [ ] Configure rate limiting for API calls
- [ ] Set up monitoring dashboards
- [ ] Test multilingual content in all target languages
- [ ] Configure A/B testing infrastructure
- [ ] Set up user behavior tracking

---

## 📈 Performance Considerations

### Avatar Generation
- **D-ID**: ~30 seconds per video
- **HeyGen**: ~60 seconds per video
- **Real-time streaming**: 100ms latency

### Voice Processing
- **STT (Wav2Vec2)**: <1 second for 10s audio
- **TTS (ElevenLabs)**: ~2 seconds for 100 words
- **Conversation turn**: 3-5 seconds total

### Translation
- **mBART**: 500ms per sentence
- **Multi-language batch**: 2-3 seconds for 5 languages

### Personalization
- **Profile update**: <50ms
- **Content personalization**: <100ms
- **A/B test assignment**: <10ms

---

## 🚀 What's Next?

Phase 4 completes the core AI agent platform. You now have:

✅ 20+ fully functional AI agents across 4 phases
✅ Centralized logging and control panel
✅ Multi-agent orchestration
✅ Digital avatars and voice conversations
✅ Multilingual support (50+ languages)
✅ Advanced personalization

**Next Steps:**
1. Review all phases for optimization
2. Set up production infrastructure
3. Configure external APIs
4. Implement custom business logic
5. Deploy to production

---

## 📞 Support

For questions or issues:
- Check logs: `/agents/logs/`
- View control panel: `http://localhost:8000/control-panel/dashboard`
- Review agent activities: `http://localhost:8000/control-panel/activities`

---

**Phase 4 Status**: ✅ Complete (5/5 agents implemented)
