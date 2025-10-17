# Agent Development Guide

## Introduction

This guide will teach you how to develop custom voice agents for the BrainCX Voice SaaS platform. By the end, you'll understand how to create agents with custom behaviors, function tools, and integrations.

## Agent Basics

### What is an Agent?

An agent is an AI-powered voice assistant that can:
- Listen to user speech (Speech-to-Text)
- Understand intent (Language Model)
- Perform actions (Function Tools)
- Respond with voice (Text-to-Speech)

### Agent Configuration

Each agent has the following configuration:

```python
{
    "name": "Customer Support Agent",
    "system_prompt": "You are a helpful customer support agent...",
    "llm_model": "gpt-4o-mini",
    "temperature": 0.7,
    "locale": "en-US",
    "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM"
}
```

**Key Parameters:**
- **name**: Display name for the agent
- **system_prompt**: Instructions that define agent behavior
- **llm_model**: OpenAI model to use (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
- **temperature**: 0.0 (focused) to 1.0 (creative)
- **locale**: Language/locale for speech recognition
- **elevenlabs_voice_id**: Voice for text-to-speech

## Creating Your First Agent

### Step 1: Define the Purpose

Example: Create a "Restaurant Reservation Agent" that helps users book tables.

### Step 2: Write the System Prompt

```text
You are a friendly restaurant reservation assistant for "Luigi's Italian Restaurant".

Your responsibilities:
- Greet customers warmly
- Ask for: party size, date, time, and name
- Confirm reservation details
- Provide the restaurant address when asked: 123 Main St, San Francisco

Restaurant Information:
- Open hours: 5 PM - 11 PM daily
- Cuisine: Italian
- Specialties: Pasta, Pizza, Seafood

Always be friendly, professional, and helpful. If the user asks for something you cannot do, politely explain your limitations.
```

### Step 3: Create via API or UI

**Via API:**
```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Restaurant Reservation Agent",
    "system_prompt": "You are a friendly restaurant reservation assistant...",
    "llm_model": "gpt-4o-mini",
    "temperature": 0.7
  }'
```

**Via UI:**
1. Go to http://localhost:3000/agents
2. Click "Create Agent"
3. Fill in the form
4. Click "Create Agent"

### Step 4: Test the Agent

1. Go to http://localhost:3000/call
2. Select your agent
3. Click "Start Voice Call"
4. Test various scenarios

## Function Tools

Function tools allow your agent to perform actions beyond conversation.

### Built-in Function Tools

The starter kit includes two example function tools:

#### 1. Weather Tool

```python
@function_tool()
async def get_weather(
    self,
    context: RunContext,
    location: Annotated[str, "The city and state, e.g. San Francisco, CA"],
) -> str:
    """Get the current weather in a given location"""
    # Implementation...
    return f"Weather in {location}: Sunny, 75°F"
```

**Usage in conversation:**
- User: "What's the weather in New York?"
- Agent calls `get_weather("New York, NY")`
- Agent: "The weather in New York is sunny with a temperature of 75°F."

#### 2. Calculator Tool

```python
@function_tool()
async def calculate(
    self,
    context: RunContext,
    expression: Annotated[str, "Mathematical expression like '2 + 2'"],
) -> str:
    """Perform a mathematical calculation"""
    result = eval(expression)  # Simplified
    return f"The result is {result}"
```

**Usage in conversation:**
- User: "What's 25 times 4?"
- Agent calls `calculate("25 * 4")`
- Agent: "The result is 100"

### Creating Custom Function Tools

Let's create a "Check Reservation" tool:

```python
@function_tool()
async def check_reservation(
    self,
    context: RunContext,
    name: Annotated[str, "Customer's full name"],
    phone: Annotated[str, "Customer's phone number"],
) -> str:
    """Check if a reservation exists"""
    # In production, query your database
    # For this example, we'll simulate
    
    reservations = {
        "John Smith": {
            "date": "2024-01-15",
            "time": "7:00 PM",
            "party_size": 4
        }
    }
    
    if name in reservations:
        res = reservations[name]
        return f"Yes, I found a reservation for {name} on {res['date']} at {res['time']} for {res['party_size']} people."
    else:
        return f"I couldn't find a reservation under the name {name}."
```

**To add this tool:**

1. Open `app/agent/simple_agent.py`
2. Add the function inside the `BrainCXAgent` class
3. Restart the agent worker

### Function Tool Best Practices

1. **Clear Descriptions**: The docstring becomes the tool description for the LLM
2. **Type Annotations**: Use `Annotated` to describe parameters
3. **Error Handling**: Always handle errors gracefully
4. **Return Strings**: Return human-readable strings
5. **Async Functions**: Use `async def` for all tools

## Advanced Agent Patterns

### Multi-Step Workflows

For complex workflows, guide the agent through steps:

```text
System Prompt:
You are a medical appointment scheduler. Follow these steps:

1. Greet the patient warmly
2. Ask for their full name
3. Ask for their date of birth (for verification)
4. Ask what type of appointment they need
5. Offer available dates and times
6. Confirm all details before booking
7. Provide confirmation number

Always complete all steps before ending the call.
```

### Context Awareness

Use the conversation context to make intelligent decisions:

```text
System Prompt:
You are a technical support agent. Remember details from earlier in the conversation.

If the user mentions a problem:
- Ask clarifying questions
- Remember their device type, OS, etc.
- Provide relevant solutions
- Follow up on previous issues
```

### Personality and Tone

Define clear personality traits:

```text
System Prompt:
You are "Max", a friendly and enthusiastic sales assistant.

Personality traits:
- Upbeat and positive
- Use conversational language
- Occasionally use appropriate emojis in responses
- Show genuine interest in helping customers
- Never pushy or aggressive

Example responses:
- "That's awesome! I'd love to help you find the perfect product."
- "Great question! Let me explain that for you."
```

## Testing Your Agent

### Test Scenarios

Create a test script with various scenarios:

1. **Happy Path**: User provides all information correctly
2. **Missing Information**: User forgets to provide details
3. **Unclear Input**: User provides ambiguous information
4. **Error Cases**: Request something impossible
5. **Edge Cases**: Unusual but valid requests

### Example Test Script

```
Test 1: Weather Query
User: "What's the weather in San Francisco?"
Expected: Agent calls get_weather() and provides weather info

Test 2: Calculator
User: "What's 100 divided by 4?"
Expected: Agent calls calculate() and says "25"

Test 3: Ambiguous Request
User: "What's the temperature?"
Expected: Agent asks "Which location would you like to know about?"

Test 4: Unsupported Request
User: "Book me a flight to Paris"
Expected: Agent politely explains it cannot book flights
```

## Debugging Tips

### 1. Check Agent Logs

The agent outputs detailed logs:

```bash
# If running with Docker
docker compose logs -f agent

# If running locally
# Check terminal where you ran python simple_agent.py
```

### 2. Test System Prompt

Test your system prompt with ChatGPT first to see how it behaves.

### 3. Monitor API Calls

Check the API logs to see session creation and agent loading:

```bash
docker compose logs -f api
```

### 4. Common Issues

**Agent Not Responding:**
- Check LiveKit credentials
- Verify OpenAI API key
- Check agent logs for errors

**Wrong Behavior:**
- Review system prompt
- Check temperature setting (lower = more focused)
- Test with different phrasings

**Function Not Called:**
- Check function docstring
- Ensure parameter types are clear
- Verify function is registered

## Performance Optimization

### 1. Model Selection

- **gpt-4o**: Most capable, slowest, most expensive
- **gpt-4o-mini**: Good balance (recommended for starter)
- **gpt-3.5-turbo**: Fastest, cheapest, less capable

### 2. Temperature Tuning

- **0.0-0.3**: Focused, consistent, predictable
- **0.4-0.7**: Balanced (recommended)
- **0.8-1.0**: Creative, varied, less predictable

### 3. Prompt Engineering

Keep prompts concise but clear:

```text
❌ Too Vague:
"You are a helpful assistant."

✓ Good:
"You are a customer support agent for TechCo. Help users with product questions, troubleshooting, and order status."

✓ Better:
"You are a customer support agent for TechCo.

Your role:
- Answer product questions about our software products
- Help troubleshoot common issues
- Check order status using the check_order tool
- Escalate complex issues to human agents

Available products:
- TechCo Pro ($99/mo): Full feature set
- TechCo Starter ($29/mo): Basic features

Always be professional, patient, and helpful."
```

## Next Steps

1. **Review Example Agents**: Check `docs/EXAMPLE_AGENTS.md`
2. **Explore API Reference**: See `docs/API_REFERENCE.md`
3. **Build Custom Integrations**: See `docs/ADVANCED_FEATURES.md`
4. **Deploy to Production**: See main `README.md`

## Resources

- **LiveKit Agents Docs**: https://docs.livekit.io/agents/
- **OpenAI API**: https://platform.openai.com/docs
- **Prompt Engineering Guide**: https://platform.openai.com/docs/guides/prompt-engineering

---

Happy agent building! 🤖

