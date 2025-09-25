# Pipecat Agent Builder - Quick Start Guide

Get your first AI agent built and deployed in under 10 minutes!

## 🚀 Installation

### 1. Prerequisites

- **Python 3.10+** installed
- **Docker** installed and running
- **Git** for cloning

### 2. Clone and Setup

```bash
# Clone the repository
cd /Users/franksimpson/CascadeProjects/docs-2/pipecat-agent-builder

# Install dependencies and setup
make setup
# OR manually:
# pip install -r requirements.txt
# python setup.py
```

### 3. Configure API Keys

Copy the environment template and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required for basic functionality
OPENAI_API_KEY=your_openai_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
CARTESIA_API_KEY=your_cartesia_api_key

# Optional for deployment
PIPECAT_CLOUD_API_KEY=your_pipecat_cloud_api_key
DAILY_API_KEY=your_daily_api_key
DOCKER_HUB_USERNAME=your_docker_username
```

**Get API Keys:**
- [OpenAI](https://platform.openai.com/api-keys) - For LLM processing
- [Deepgram](https://console.deepgram.com/) - For speech-to-text
- [Cartesia](https://play.cartesia.ai/) - For text-to-speech
- [Pipecat Cloud](https://pipecat.daily.co/) - For deployment (optional)

## 🎯 Build Your First Agent

### Option 1: Interactive Conversation (Recommended)

Start the conversational interface:

```bash
python main.py
```

Then:
1. Open `http://localhost:7860` in your browser
2. Allow microphone access
3. Click "Connect" and start talking!

**Example conversation:**
> "I want to build a customer service bot that can handle phone calls in English and Spanish, access our FAQ database, and integrate with Zendesk."

The system will guide you through gathering all requirements and automatically generate your agent.

### Option 2: Quick Test

Run the system test to verify everything works:

```bash
python test_system.py
```

## 🏗️ What Gets Built

The system generates a complete Pipecat agent with:

### Generated Files
```
generated_agents/your_agent_name/
├── bot.py                 # Main agent code
├── Dockerfile            # Container configuration
├── requirements.txt      # Python dependencies
├── pcc-deploy.toml      # Pipecat Cloud config
├── .env.example         # Environment template
└── knowledge_processor.py # Knowledge integration (if needed)
```

### Key Features
- **Voice Interface**: Real-time speech recognition and synthesis
- **Multi-language Support**: Configurable language support
- **Knowledge Integration**: Automatic FAQ/document processing
- **Cloud Deployment**: Ready for Pipecat Cloud deployment
- **Monitoring**: Built-in metrics and logging

## 🚀 Deployment Options

### Local Testing
```bash
cd generated_agents/your_agent_name
python bot.py
# Open http://localhost:7860 to test
```

### Pipecat Cloud (Recommended)
The system can automatically deploy to Pipecat Cloud:

1. **During Build**: Say "yes" when prompted to deploy
2. **Manual Deploy**: 
   ```bash
   cd generated_agents/your_agent_name
   pcc deploy
   ```

### Self-Hosted
```bash
cd generated_agents/your_agent_name
docker build -t my-agent .
docker run -p 8000:8000 --env-file .env my-agent
```

## 🎮 Example Use Cases

### Customer Service Bot
```
"Build a customer service agent that handles phone calls, 
speaks English and Spanish, accesses our FAQ database, 
and can escalate to human agents through Zendesk integration."
```

### Personal Assistant
```
"Create a personal assistant for web and mobile that can 
schedule meetings, answer questions about my documents, 
and has a friendly, professional personality."
```

### Educational Tutor
```
"Build an educational tutor that helps students with math, 
can access Khan Academy content, works on web browsers, 
and adapts to different learning styles."
```

## 🔧 Advanced Configuration

### Custom Knowledge Sources

Add knowledge sources during conversation or modify the generated `knowledge_processor.py`:

```python
# Web scraping
{"type": "web", "source": "https://docs.yourcompany.com"}

# Document processing  
{"type": "document", "source": "/path/to/faq.pdf"}

# API integration
{"type": "api", "source": "https://api.yourservice.com"}
```

### Service Customization

The system supports 80+ AI services. Popular combinations:

**High Quality (Premium)**
- STT: Deepgram Nova-2
- LLM: OpenAI GPT-4o
- TTS: ElevenLabs

**Cost Optimized**
- STT: OpenAI Whisper
- LLM: OpenAI GPT-4o-mini
- TTS: OpenAI TTS

**Low Latency**
- STT: Deepgram Nova-2
- LLM: Groq Llama
- TTS: Cartesia Sonic

### Windsurf Cascade Integration

If you have Windsurf Cascade available via MCP:

```bash
# Set MCP endpoint in .env
MCP_SERVER_URL=ws://localhost:8765
WINDSURF_CASCADE_ENDPOINT=your_cascade_endpoint
```

This enables advanced code generation, validation, and optimization.

## 🐛 Troubleshooting

### Common Issues

**"Missing API keys"**
- Check your `.env` file has all required keys
- Verify API keys are valid and have sufficient credits

**"Docker not found"**
- Install Docker Desktop
- Ensure Docker is running: `docker --version`

**"Vectorization failed"**
- Check disk space (needs ~500MB for documentation)
- Verify docs path in settings: `/Users/franksimpson/CascadeProjects/docs-2`

**"Connection failed"**
- Check microphone permissions in browser
- Try different browser (Chrome/Firefox recommended)
- Disable VPN if connection issues persist

### Getting Help

1. **Check Logs**: `tail -f logs/pipecat_builder.log`
2. **Run Tests**: `python test_system.py`
3. **Discord**: [Pipecat Community](https://discord.gg/pipecat)
4. **GitHub Issues**: Report bugs and feature requests

## 📚 Next Steps

- **Explore Examples**: Check `generated_agents/` for inspiration
- **Read Documentation**: Full docs in the main README.md
- **Join Community**: Connect with other builders on Discord
- **Contribute**: Submit improvements and new features

## 🎉 Success!

You now have a complete AI agent building system! The conversational interface makes it easy to create sophisticated voice AI applications without deep technical knowledge.

**What's Next?**
- Build agents for different use cases
- Experiment with different AI service combinations  
- Deploy to production on Pipecat Cloud
- Share your creations with the community!
