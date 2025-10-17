# BrainCX Voice SaaS - Starter Kit Guide

## 📦 What's Included

This starter kit contains everything you need to learn and build AI-powered voice agents:

### Core Components

1. **Backend API (FastAPI)**
   - Agent management (CRUD operations)
   - Session tracking and management
   - LiveKit integration
   - RESTful API with automatic documentation

2. **Voice Agent Worker (Python)**
   - LiveKit Agents framework integration
   - OpenAI GPT integration
   - Deepgram speech-to-text
   - ElevenLabs text-to-speech
   - Example function tools (weather, calculator)

3. **Frontend (React)**
   - Agent management interface
   - Session monitoring dashboard
   - Voice call interface
   - Responsive design

4. **Database (PostgreSQL)**
   - Agent configurations
   - Session records
   - Organization/tenant support

5. **Documentation**
   - Quick Start Guide
   - Agent Development Guide
   - API Reference
   - Architecture Guide
   - Advanced Features

### File Structure

```
starter-kit-braincx-voice-saas/
├── README.md                          # Main readme with overview
├── STARTER_KIT_GUIDE.md              # This file
├── .gitignore                         # Git ignore patterns
│
├── app/
│   ├── api/                           # Backend API
│   │   ├── main.py                    # FastAPI application
│   │   ├── models.py                  # Database models
│   │   ├── database.py                # DB connection
│   │   ├── migrate.py                 # Database migrations
│   │   ├── Dockerfile                 # API container
│   │   └── requirements.txt           # Python dependencies
│   │
│   ├── agent/                         # Voice agent
│   │   ├── simple_agent.py            # Agent implementation
│   │   ├── Dockerfile                 # Agent container
│   │   └── requirements.txt           # Python dependencies
│   │
│   ├── web/                           # Frontend
│   │   ├── src/
│   │   │   ├── App.js                 # Main app component
│   │   │   ├── api.js                 # API client
│   │   │   └── components/            # React components
│   │   │       ├── AgentManager.js    # Agent CRUD
│   │   │       ├── SessionsList.js    # Session history
│   │   │       └── VoiceCall.js       # Voice call UI
│   │   ├── Dockerfile                 # Web container
│   │   └── package.json               # Node dependencies
│   │
│   └── infra/                         # Infrastructure
│       ├── docker-compose.yml         # Orchestration
│       ├── ENV_SETUP.md              # Environment config guide
│       └── Caddyfile                  # Reverse proxy (optional)
│
└── docs/                              # Documentation
    ├── ARCHITECTURE.md                # System architecture
    ├── QUICK_START.md                 # 15-minute setup guide
    ├── AGENT_DEVELOPMENT.md           # Agent development guide
    ├── API_REFERENCE.md               # Complete API docs
    └── ADVANCED_FEATURES.md           # Advanced topics
```

## 🎯 Learning Objectives

By working with this starter kit, you will learn:

### Beginner Level
- ✅ How voice AI agents work
- ✅ How to create and configure agents
- ✅ How to test voice calls
- ✅ Basic Docker and Docker Compose
- ✅ REST API fundamentals

### Intermediate Level
- ✅ Agent development with LiveKit
- ✅ System prompt engineering
- ✅ Function tool development
- ✅ React application structure
- ✅ Database modeling with SQLAlchemy
- ✅ Async Python programming

### Advanced Level
- ✅ Real-time voice processing
- ✅ WebRTC and media streaming
- ✅ Multi-service architecture
- ✅ API integration patterns
- ✅ Production deployment strategies

## 🚀 Getting Started

### Step 1: Read the Documentation

**Start here:**
1. `README.md` - Overview and introduction
2. `docs/QUICK_START.md` - 15-minute setup guide
3. `docs/ARCHITECTURE.md` - Understanding the system

### Step 2: Set Up Your Environment

Follow the Quick Start guide to:
1. Get API keys (LiveKit, OpenAI, Deepgram, ElevenLabs)
2. Configure environment variables
3. Start the platform with Docker Compose
4. Access the web interface

**Time estimate**: 15-20 minutes

### Step 3: Create Your First Agent

1. Open http://localhost:3000/agents
2. Create an agent with a simple system prompt
3. Test it with a voice call
4. Experiment with different prompts and settings

**Time estimate**: 10 minutes

### Step 4: Explore the Code

**Backend (Python/FastAPI)**
- Start with: `app/api/main.py`
- Look at: `app/api/models.py`
- Understand: RESTful API design

**Agent (Python/LiveKit)**
- Start with: `app/agent/simple_agent.py`
- Look at: Function tool examples
- Understand: Agent lifecycle

**Frontend (React)**
- Start with: `app/web/src/App.js`
- Look at: `app/web/src/components/VoiceCall.js`
- Understand: WebRTC integration

**Time estimate**: 1-2 hours

### Step 5: Follow the Learning Path

**Week 1: Fundamentals**
- Understand the architecture
- Create multiple agents
- Test different configurations
- Read `docs/AGENT_DEVELOPMENT.md`

**Week 2: Agent Development**
- Modify the example agent
- Create custom function tools
- Integrate with external APIs
- Test edge cases

**Week 3: Frontend Development**
- Customize the React UI
- Add new components
- Improve user experience
- Study `app/web/src/`

**Week 4: Backend Development**
- Add new API endpoints
- Modify database models
- Implement new features
- Study `app/api/`

**Week 5-6: Advanced Topics**
- Read `docs/ADVANCED_FEATURES.md`
- Implement phone calling
- Add analytics
- Deploy to production

## 💡 Example Use Cases

### 1. Customer Support Agent
```
System Prompt:
"You are a helpful customer support agent for TechCo.
Help users with product questions and troubleshooting.
Be patient, professional, and empathetic."

Function Tools:
- check_order_status(order_id)
- search_knowledge_base(query)
- create_support_ticket(issue, priority)
```

### 2. Restaurant Reservation Agent
```
System Prompt:
"You are a reservation agent for Luigi's Italian Restaurant.
Help customers book tables and answer questions about the menu.
Opening hours: 5 PM - 11 PM daily."

Function Tools:
- check_availability(date, time, party_size)
- create_reservation(name, phone, details)
- get_menu()
```

### 3. Personal Assistant
```
System Prompt:
"You are a personal assistant that helps with daily tasks.
You can check weather, set reminders, and provide information.
Be friendly and efficient."

Function Tools:
- get_weather(location)
- calculate(expression)
- search_web(query)
- remember_note(content)
```

## 🎓 Training Exercises

### Exercise 1: Basic Agent Creation
**Goal**: Create 3 different agents with distinct personalities
**Time**: 30 minutes
**Skills**: System prompt engineering, agent configuration

### Exercise 2: Function Tool Development
**Goal**: Create a function tool that calls an external API
**Time**: 1 hour
**Skills**: Python async, API integration

### Exercise 3: UI Customization
**Goal**: Add a new page to the React application
**Time**: 2 hours
**Skills**: React, component design

### Exercise 4: Database Integration
**Goal**: Add a new database table and API endpoints
**Time**: 2 hours
**Skills**: SQLAlchemy, FastAPI, migrations

### Exercise 5: End-to-End Feature
**Goal**: Build a complete feature from database to UI
**Time**: 4-6 hours
**Skills**: Full-stack development

## 🔍 What's NOT Included

This starter kit is simplified for learning. The following production features are not included:

- ❌ Authentication (only basic admin password)
- ❌ Multi-tenancy (single organization)
- ❌ Payment processing
- ❌ Advanced analytics
- ❌ Phone number provisioning
- ❌ Production monitoring
- ❌ Advanced security features
- ❌ Kubernetes deployment configs
- ❌ CI/CD pipelines
- ❌ Comprehensive testing

These are intentionally omitted to keep the learning focus clear.

## 📊 Comparing to Production

| Feature | Starter Kit | Production |
|---------|------------|------------|
| Authentication | Basic | OAuth, JWT, MFA |
| Multi-tenancy | Single org | Full multi-tenant |
| Database | SQLite/Postgres | Postgres + Redis |
| Scaling | Single instance | Auto-scaling |
| Monitoring | Logs only | Full observability |
| Security | Basic | Enterprise-grade |
| Cost Tracking | Simple | Detailed analytics |
| Phone Calls | Manual setup | Automated provisioning |

## 🛠️ Customization Guide

### Adding a New Function Tool

1. Open `app/agent/simple_agent.py`
2. Add your function inside the agent class:

```python
@function_tool()
async def your_function(
    self,
    context: RunContext,
    param: Annotated[str, "Description"],
) -> str:
    """Function description for the LLM"""
    # Your logic here
    return "Result"
```

3. Restart the agent: `docker compose restart agent`

### Adding a New API Endpoint

1. Open `app/api/main.py`
2. Add your endpoint:

```python
@app.get("/your-endpoint")
def your_endpoint(db: Session = Depends(get_db)):
    # Your logic here
    return {"data": "value"}
```

3. Restart the API: `docker compose restart api`

### Adding a New UI Component

1. Create `app/web/src/components/YourComponent.js`
2. Import and use in `App.js`
3. Rebuild: `docker compose up -d --build web`

## 📚 Additional Resources

### Documentation
- All docs are in the `docs/` folder
- API docs: http://localhost:8000/docs
- This guide: `STARTER_KIT_GUIDE.md`

### External Resources
- **LiveKit**: https://docs.livekit.io
- **OpenAI**: https://platform.openai.com/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **React**: https://react.dev

### Getting Help
- Check the documentation first
- Review the code comments
- Check Docker logs: `docker compose logs -f`
- Test with API docs: http://localhost:8000/docs

## 🎯 Success Criteria

You've mastered this starter kit when you can:

✅ Create and configure agents independently
✅ Develop custom function tools
✅ Modify the frontend to add new features
✅ Add new API endpoints
✅ Understand the full request/response flow
✅ Debug issues using logs
✅ Deploy with Docker Compose
✅ Explain the architecture to someone else

## 🚢 Next Steps: Production

When you're ready for production:

1. **Security**: Implement proper authentication
2. **Scaling**: Use Kubernetes or similar
3. **Monitoring**: Add Prometheus, Grafana
4. **Database**: Use managed PostgreSQL
5. **Secrets**: Use secrets management (AWS Secrets Manager, etc.)
6. **CI/CD**: Set up automated deployments
7. **Testing**: Add comprehensive tests
8. **Documentation**: Document your customizations

## 💬 Final Notes

This starter kit is designed to teach you the fundamentals of building voice AI agents. It's simplified to focus on learning, not production deployment.

**Use it to**:
- ✅ Learn voice AI development
- ✅ Prototype new features
- ✅ Train your team
- ✅ Evaluate the technology

**Don't use it for**:
- ❌ Production deployment (without modifications)
- ❌ Processing sensitive data (without security enhancements)
- ❌ High-scale applications (without optimization)

**Most importantly**: Have fun and experiment! The best way to learn is by building.

---

**Questions or feedback?** Review the documentation or examine the code for answers.

Happy learning! 🚀

