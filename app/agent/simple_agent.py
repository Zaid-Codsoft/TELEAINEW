#!/usr/bin/env python3
"""
BrainCX Voice Agent - Simplified Starter Kit Version
Handles web-based voice calls with basic functionality
"""
from dotenv import load_dotenv
import json
import os
import aiohttp
from typing import Annotated
from livekit import api
from livekit.agents import function_tool, RunContext

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    deepgram,
    elevenlabs,
    silero,
)

# Load environment variables
load_dotenv('.env.local')

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

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


async def get_agent_config(room_name: str) -> dict:
    """
    Fetch agent configuration from the API based on room name
    
    Args:
        room_name: LiveKit room name
        
    Returns:
        Dictionary with agent configuration
    """
    try:
        # Try to get agent config from API
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/agents") as response:
                if response.status == 200:
                    agents_list = await response.json()
                    if agents_list:
                        # Use the first active agent
                        for agent in agents_list:
                            if agent.get("is_active", True):
                                print(f"✓ Loaded agent: {agent['name']}")
                                return agent
                        # If no active agent, use first one
                        return agents_list[0]
    except Exception as e:
        print(f"⚠ Could not fetch agent config from API: {e}")
    
    # Fallback to default configuration
    print("⚠ Using default agent configuration")
    return {
        "name": "Demo Assistant",
        "system_prompt": (
            "You are a friendly and helpful voice assistant. "
            "You can help users with general questions, check the weather, "
            "and perform calculations. Always be polite, clear, and concise."
        ),
        "llm_model": "gpt-4o-mini",
        "temperature": 0.7,
        "locale": "en-US",
        "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM"
    }


async def entrypoint(ctx: agents.JobContext):
    """
    Main entrypoint for the voice agent
    Called when a new session/call starts
    """
    print(f"🎯 Agent job started for room: {ctx.room.name}")
    
    # Connect to the LiveKit room
    await ctx.connect()
    
    # Get agent configuration
    agent_config = await get_agent_config(ctx.room.name)
    
    # Create agent session with plugins
    print("🔧 Initializing agent session...")
    session = AgentSession(
        stt=deepgram.STT(
            model="nova-2",
            language=agent_config.get("locale", "en-US")
        ),
        llm=openai.LLM(
            model=agent_config.get("llm_model", "gpt-4o-mini"),
            temperature=agent_config.get("temperature", 0.7)
        ),
        tts=elevenlabs.TTS(
            voice_id=agent_config.get("elevenlabs_voice_id", "21m00Tcm4TlvDq8ikWAM")
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
    print("🚀 BrainCX Voice Agent - Starting...")
    print("=" * 60)
    print(f"API URL: {API_BASE_URL}")
    print(f"LiveKit: {os.getenv('LIVEKIT_URL', 'Not configured')}")
    print("=" * 60)
    
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name=os.getenv("AGENT_NAME", "braincx-starter-agent")
        )
    )

