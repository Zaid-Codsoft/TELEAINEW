# Environment Configuration Guide

## Setup Instructions

1. Copy the content below to a file named `.env` in this directory
2. Replace all placeholder values with your actual credentials
3. **NEVER commit .env to version control!**

## Environment Variables Template

```bash
# ============================================
# BrainCX Voice SaaS - Environment Configuration
# ============================================

# ============================================
# DATABASE CONFIGURATION
# ============================================
POSTGRES_USER=braincx
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=braincx
DATABASE_URL=postgresql://braincx:your_secure_password_here@db:5432/braincx

# ============================================
# LIVEKIT CONFIGURATION
# ============================================
# Get these from: https://cloud.livekit.io
LIVEKIT_URL=wss://your-livekit-instance.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxxxxxxx
LIVEKIT_API_SECRET=your_livekit_api_secret

# ============================================
# AUTHENTICATION
# ============================================
ADMIN_PASSWORD=changeme_in_production
SESSION_SECRET=your-random-secret-key-here-min-32-chars

# ============================================
# OPENAI CONFIGURATION
# ============================================
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# DEEPGRAM CONFIGURATION (Speech-to-Text)
# ============================================
# Get your API key from: https://console.deepgram.com/
DEEPGRAM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# ELEVENLABS CONFIGURATION (Text-to-Speech)
# ============================================
# Get your API key from: https://elevenlabs.io/app/settings/api-keys
ELEVENLABS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# TWILIO CONFIGURATION (Optional - for phone calls)
# ============================================
# Get these from: https://console.twilio.com/
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_SIP_TRUNK_ID=

# ============================================
# TELNYX CONFIGURATION (Alternative to Twilio)
# ============================================
# Get these from: https://portal.telnyx.com/
TELNYX_API_KEY=KEYxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TELNYX_PUBLIC_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TELNYX_SIP_CONNECTION_ID=

# ============================================
# AGENT CONFIGURATION
# ============================================
AGENT_NAME=braincx-starter-agent
DEFAULT_LLM_MODEL=gpt-4o-mini
DEFAULT_TEMPERATURE=0.7
DEFAULT_LOCALE=en-US
DEFAULT_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# ============================================
# FRONTEND CONFIGURATION
# ============================================
REACT_APP_API_URL=http://localhost:8000

# ============================================
# OPTIONAL SERVICES
# ============================================
# OpenWeather (for weather agent example)
OPENWEATHER_API_KEY=

# Pinecone (for knowledge bases)
PINECONE_API_KEY=
PINECONE_ENVIRONMENT=

# ============================================
# DEVELOPMENT/PRODUCTION MODE
# ============================================
ENVIRONMENT=development
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

## Service-Specific Configuration

### For API Backend (`app/api/.env.local`)

Create a file `app/api/.env.local` with:

```bash
DATABASE_URL=postgresql://braincx:yourpassword@localhost:5432/braincx
LIVEKIT_URL=wss://your-livekit-instance.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxxxxxxx
LIVEKIT_API_SECRET=your_livekit_api_secret
ADMIN_PASSWORD=changeme
SESSION_SECRET=your-secret-key-here
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPGRAM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ELEVENLABS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TELNYX_API_KEY=KEYxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### For Agent Worker (`app/agent/.env.local`)

Create a file `app/agent/.env.local` with:

```bash
LIVEKIT_URL=wss://your-livekit-instance.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxxxxxxx
LIVEKIT_API_SECRET=your_livekit_api_secret
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPGRAM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ELEVENLABS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
API_BASE_URL=http://api:8000
AGENT_NAME=braincx-starter-agent
OPENWEATHER_API_KEY=
```

### For Web Frontend (`app/web/.env.local`)

Create a file `app/web/.env.local` with:

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_DEBUG=true
```

## Getting API Keys

### LiveKit
1. Visit https://cloud.livekit.io
2. Sign up for free account
3. Create a new project
4. Copy API Key and API Secret from settings

### OpenAI
1. Visit https://platform.openai.com
2. Sign up and add payment method
3. Go to API Keys section
4. Create new secret key

### Deepgram
1. Visit https://console.deepgram.com
2. Sign up for free account ($200 credit)
3. Go to API Keys
4. Create new key

### ElevenLabs
1. Visit https://elevenlabs.io
2. Sign up for free account
3. Go to Profile → API Keys
4. Create new key

### Twilio (Optional)
1. Visit https://console.twilio.com
2. Sign up for account ($15 free credit)
3. Copy Account SID and Auth Token
4. Purchase a phone number
5. Configure SIP trunk in LiveKit

### Telnyx (Optional)
1. Visit https://portal.telnyx.com
2. Sign up for account
3. Go to API Keys
4. Create new key
5. Configure SIP connection in LiveKit

## Security Notes

1. **Never** commit `.env` files to Git
2. Use strong passwords (minimum 32 characters)
3. Rotate API keys regularly
4. Use different keys for development and production
5. Add `.env*` to `.gitignore` (except `.env.example`)

