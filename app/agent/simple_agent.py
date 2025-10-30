#!/usr/bin/env python3
"""
BrainCX Voice Agent - Hugging Face Free Models Version
Uses free open-source models from Hugging Face instead of paid APIs
"""
from dotenv import load_dotenv
import os
import aiohttp
from typing import Annotated
from livekit.agents import function_tool, RunContext

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import silero

# Import our custom implementations
from hf_stt import WhisperSTT
from gemini_llm import GeminiLLM
from hf_tts import SpeechT5TTSPlugin

# Load environment variables
load_dotenv('.env.local')

# Agent configuration class
class BrainCXAgent(Agent):
    """Voice agent with configurable behavior"""
    
    def __init__(self, agent_config: dict) -> None:
        """
        Initialize agent with configuration from database
        
        Args:
            agent_config: Dictionary containing agent configuration
                - system_prompt: Instructions for the agent
                - name: Agent name
        """
        instructions = agent_config.get(
            "system_prompt",
            "You are a helpful voice AI assistant."
        )
        super().__init__(instructions=instructions)
        self.agent_name = agent_config.get("name", "Assistant")
    
    @function_tool()
    async def get_weather(
        self,
        context: RunContext,
        location: Annotated[str, "The city and state, e.g. San Francisco, CA"],
    ) -> str:
        """Get the current weather in a given location"""
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            return "I don't have access to weather data right now. Please set up the OpenWeather API key."

        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return f"Sorry, I couldn't get the weather for {location}. Please check the city name."
                
                data = await response.json()
                
                if "weather" not in data or not data["weather"]:
                    return "Sorry, I couldn't find weather data for that location."
                
                description = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                
                return (
                    f"The weather in {location} is currently {description}. "
                    f"The temperature is {temp}°C, feels like {feels_like}°C, "
                    f"with {humidity}% humidity."
                )
    
    @function_tool()
    async def calculate(
        self,
        context: RunContext,
        expression: Annotated[str, "Mathematical expression to evaluate, e.g. '2 + 2' or '10 * 5'"],
    ) -> str:
        """Perform a mathematical calculation"""
        try:
            # Simple eval for basic math (in production, use a proper math parser)
            # Sanitize input to allow only numbers and basic operators
            allowed_chars = set('0123456789+-*/().,  ')
            if not all(c in allowed_chars for c in expression):
                return "I can only calculate basic mathematical expressions with numbers and operators (+, -, *, /)."
            
            result = eval(expression)
            return f"The result of {expression} is {result}"
        except Exception as e:
            return f"I couldn't calculate that. Please provide a valid mathematical expression."


def get_agent_config() -> dict:
    """
    Get simple agent configuration with small, fast-downloading models
    
    Returns:
        Dictionary with agent configuration using smallest models
    """
    return {
        "name": "Simple Voice Assistant",
        "system_prompt": (
            "You are a friendly and helpful voice assistant. "
            "You can help users with general questions, check the weather, "
            "and perform calculations. Always be polite, clear, and concise. "
            "Keep responses brief and conversational."
        ),
        # Using Gemini for LLM, small models for STT/TTS
        "llm_model": "gemini-1.5-flash",  # Fast and efficient Gemini model
        "stt_model": "tiny",  # ~150MB - Smallest Whisper model
        "tts_model": "microsoft/speecht5_tts",  # SpeechT5 - Python 3.13 compatible
        "temperature": 0.7,
        "locale": "en-US",
    }


async def entrypoint(ctx: agents.JobContext):
    """
    Main entrypoint for the voice agent
    Called when a new session/call starts
    """
    print(f"🎯 Agent job started for room: {ctx.room.name}")
    
    # Connect to the LiveKit room
    await ctx.connect()
    
    # Get agent configuration (simplified - no API calls)
    agent_config = get_agent_config()
    
    # Create agent session with Gemini LLM and small STT/TTS models
    print("🔧 Initializing agent session...")
    
    # Extract locale for language code (e.g., "en-US" -> "en")
    locale = agent_config["locale"]
    language_code = locale.split("-")[0] if "-" in locale else locale
    
    session = AgentSession(
        stt=WhisperSTT(
            model=agent_config["stt_model"],  # tiny - smallest and fastest to download
            language=language_code,
        ),
        llm=GeminiLLM(
            model=agent_config["llm_model"],  # Gemini - fast and high quality
            api_key=os.getenv("GEMINI_API_KEY", "AIzaSyCFWCPXn92NwfoUOg4lNDG1t2Ex3MesMfQ"),
            temperature=agent_config["temperature"],
            max_tokens=1024,
        ),
        tts=SpeechT5TTSPlugin(
            model="microsoft/speecht5_tts",  # SpeechT5 - Python 3.13 compatible
        ),
        vad=silero.VAD.load(),
    )
    
    # Start the agent session
    print("▶ Starting agent session...")
    await session.start(
        room=ctx.room,
        agent=BrainCXAgent(agent_config),
        room_input_options=RoomInputOptions(),
    )
    
    # Greet the user
    greeting = (
        f"Hello! I'm {agent_config['name']}. "
        "How can I help you today?"
    )
    
    print(f"👋 Greeting user: {greeting}")
    await session.generate_reply(
        instructions=f"Say exactly: '{greeting}'"
    )
    
    print("✓ Agent is now active and listening...")


if __name__ == "__main__":
    """
    Run the agent worker
    Usage:
        python simple_agent.py dev              # Development mode
        python simple_agent.py start            # Production mode
    """
    print("=" * 60)
    print("🚀 Simple Voice Agent - Starting...")
    print("Using smallest models for fast downloads")
    print("=" * 60)
    print(f"LiveKit: {os.getenv('LIVEKIT_URL', 'Not configured')}")
    print("=" * 60)
    
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name=os.getenv("AGENT_NAME", "braincx-starter-agent")
        )
    )

