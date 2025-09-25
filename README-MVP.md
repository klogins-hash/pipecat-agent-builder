# Pipecat Agent Builder - MVP

**Simple, fast agent creation for testing and iteration.**

## 🚀 Quick Start (MVP)

```bash
# 1. Install minimal dependencies
pip install -r requirements-mvp.txt

# 2. Set up environment (optional)
cp .env.example .env
# Add API keys if you have them

# 3. Create a sample agent
python mvp_main.py --sample

# 4. Or use interactive mode
python mvp_main.py --interactive
```

## 🎯 MVP Features

### ✅ **What's Included**
- **Core Agent Generation** - Creates complete Pipecat agents
- **Template System** - Production-ready code templates
- **Knowledge Integration** - Optional docs vectorization
- **Basic Deployment** - Docker + Pipecat Cloud configs
- **Simple Interface** - Programmatic and interactive modes

### ❌ **What's Removed (For Speed)**
- Complex input validation
- Enterprise security features
- Production monitoring
- Resource management
- Comprehensive error handling
- Extensive testing suite

## 📁 Project Structure (MVP)

```
pipecat-agent-builder/
├── mvp_main.py              # Main MVP interface
├── core/
│   ├── simple_config.py     # Simplified configuration
│   └── logger.py           # Basic logging
├── knowledge/              # Documentation vectorization
├── generation/             # Code templates
├── deployment/             # Deployment automation
├── archive/                # Archived production features
│   └── production-features/ # Enterprise features
└── generated_agents/       # Your created agents
```

## 🛠️ Usage Examples

### Programmatic Usage

```python
from mvp_main import SimplePipecatAgentBuilder
from core.simple_config import AgentRequirements, AIServiceConfig

# Define your agent
requirements = AgentRequirements(
    name="My Customer Bot",
    description="Handles customer inquiries",
    use_case="customer_service",
    channels=["web", "phone"],
    languages=["en"],
    stt_service=AIServiceConfig(name="deepgram", provider="deepgram"),
    llm_service=AIServiceConfig(name="openai", provider="openai"),
    tts_service=AIServiceConfig(name="cartesia", provider="cartesia")
)

# Build the agent
builder = SimplePipecatAgentBuilder()
await builder.initialize()
result = await builder.build_agent(requirements)

print(f"Agent created at: {result['agent_directory']}")
```

### Interactive Mode

```bash
python mvp_main.py --interactive
```

Follow the prompts to create your agent!

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Optional - only needed if using specific services
OPENAI_API_KEY=your_key_here
DEEPGRAM_API_KEY=your_key_here
CARTESIA_API_KEY=your_key_here
```

### Agent Requirements

```python
AgentRequirements(
    name="Agent Name",                    # Required
    description="What it does",           # Required
    use_case="customer_service",          # Required
    channels=["web", "phone"],            # Optional, default: ["web"]
    languages=["en", "es"],               # Optional, default: ["en"]
    # AI services (optional - will use defaults)
    stt_service=AIServiceConfig(...),
    llm_service=AIServiceConfig(...),
    tts_service=AIServiceConfig(...),
    # Knowledge and integrations (optional)
    knowledge_sources=[...],
    integrations=[...]
)
```

## 📦 Generated Agent Structure

Each agent gets its own directory with:

```
generated_agents/my_agent/
├── bot.py                  # Main agent code
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── pcc-deploy.toml        # Pipecat Cloud deployment
├── .env.example           # Environment template
└── knowledge_processor.py # Knowledge integration (if needed)
```

## 🚀 Running Your Agent

```bash
cd generated_agents/my_agent

# Set up environment
cp .env.example .env
# Add your API keys

# Install dependencies
pip install -r requirements.txt

# Run locally
python bot.py

# Or deploy to Pipecat Cloud
pcc deploy
```

## 🔄 Upgrading to Production

When ready for production features:

```bash
# Restore enterprise features
cp archive/production-features/*.py core/
cp -r archive/production-features/tests/ .

# Use full requirements
pip install -r requirements.txt

# Switch to production main
python main.py
```

## 🎯 MVP Philosophy

**Move Fast, Break Things (Safely)**

- **Minimal Friction** - Get agents running quickly
- **Core Functionality** - Focus on what matters
- **Easy Iteration** - Fast feedback loops
- **Simple Debugging** - Clear, minimal code paths
- **Production Path** - Easy upgrade when ready

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors** - Make sure you're using `mvp_main.py` not `main.py`
2. **Missing API Keys** - Add them to `.env` or use defaults
3. **Vectorizer Issues** - It's optional, agent will still work
4. **Permission Errors** - Check directory permissions

### Getting Help

- Check `generated_agents/` for your created agents
- Look at `archive/README.md` for production features
- Use `python mvp_main.py --help` for options

## 📈 Next Steps

1. **Test Your Agent** - Run it locally first
2. **Iterate Quickly** - Modify and rebuild
3. **Gather Feedback** - See what works
4. **Scale Up** - Add production features when needed

---

**MVP Goal: Get working agents in minutes, not hours!** 🚀
