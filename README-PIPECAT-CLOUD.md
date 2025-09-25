# 🎤 Pipecat Agent Builder - Voice-Only Edition

**Build sophisticated voice AI agents through natural conversation!**

This is a voice-only Pipecat agent that helps users create custom voice AI agents through natural conversation. Users simply talk to describe their requirements, and the system generates complete, production-ready Pipecat applications.

## 🌟 **Features**

- 🎤 **Pure Voice Interface** - No web frontend needed
- 🗣️ **Natural Conversation** - Describe your agent in plain English
- 🤖 **Complete Code Generation** - Get full Pipecat applications
- 📞 **Multi-Channel Support** - Phone, web, mobile integrations
- 🌍 **Multi-Language** - Support for multiple languages
- 🎨 **Custom Personalities** - Define agent behavior and tone
- ☁️ **Pipecat Cloud Ready** - Optimized for cloud deployment

## 🚀 **Quick Start**

### **Prerequisites**

1. **Sign up for Pipecat Cloud**: [https://pipecat.daily.co/sign-up](https://pipecat.daily.co/sign-up)
2. **Get API Keys**:
   - [Deepgram](https://console.deepgram.com/signup) for Speech-to-Text
   - [OpenAI](https://auth.openai.com/create-account) for LLM inference
   - [Cartesia](https://play.cartesia.ai/sign-up) for Text-to-Speech
3. **Install Docker**: [https://www.docker.com/](https://www.docker.com/)
4. **Create Docker Hub account**: [https://hub.docker.com/](https://hub.docker.com/)

### **Local Development**

```bash
# Clone the repository
git clone <your-repo-url>
cd pipecat-agent-builder

# Set up environment
cp .env.pipecat .env
# Edit .env with your API keys

# Install dependencies with uv
uv sync

# Run locally
uv run bot.py
```

Visit [http://localhost:7860](http://localhost:7860) and click "Connect" to start talking!

### **Deploy to Pipecat Cloud**

1. **Login to Pipecat Cloud**:
   ```bash
   uv run pcc auth login
   ```

2. **Update deployment config**:
   Edit `pcc-deploy.toml` and update the image field:
   ```toml
   image = "YOUR_DOCKERHUB_USERNAME/pipecat-agent-builder:0.1"
   ```

3. **Upload secrets**:
   ```bash
   uv run pcc secrets set agent-builder-secrets --file .env
   ```

4. **Build and deploy**:
   ```bash
   # Build and push Docker image
   uv run pcc docker build-push
   
   # Deploy to Pipecat Cloud
   uv run pcc deploy
   ```

5. **Connect to your agent**:
   - Open [Pipecat Cloud dashboard](https://pipecat.daily.co/)
   - Select "agent-builder" → Sandbox
   - Click "Connect" and start talking!

## 🎯 **How It Works**

### **User Experience**

1. **Connect** - Click "Connect" in Pipecat Cloud sandbox
2. **Describe** - "I need a customer service agent for my restaurant"
3. **Conversation** - AI asks natural follow-up questions
4. **Generation** - Complete Pipecat agent code is created
5. **Delivery** - Download ZIP or receive via email

### **Example Conversations**

**Customer Service Bot:**
> "Create a customer service agent for my e-commerce store that can track orders, handle returns, answer product questions, and escalate to humans when needed. I need it to support both English and Spanish."

**Restaurant Assistant:**
> "Build a phone agent for my Italian restaurant that takes reservations, answers menu questions, handles takeout orders, and provides directions. It should have a warm, friendly personality."

**Sales Assistant:**
> "I need a sales bot for my SaaS company that can qualify leads, schedule demos, answer pricing questions, and integrate with our CRM. It should sound professional but approachable."

## 🏗️ **Architecture**

```
Voice Input → Deepgram STT → OpenAI LLM → Agent Generation → Cartesia TTS → Voice Output
```

**Key Components:**
- **Transport**: Daily WebRTC for browser connections
- **STT**: Deepgram for speech recognition
- **LLM**: OpenAI GPT-4o for conversation and code generation
- **TTS**: Cartesia for natural speech synthesis
- **VAD**: Silero for voice activity detection
- **Pipeline**: Pipecat's frame-based processing

## 📁 **Project Structure**

```
pipecat-agent-builder/
├── bot.py                    # Main agent logic
├── pcc-deploy.toml          # Pipecat Cloud config
├── Dockerfile.pipecat       # Container config
├── pyproject.toml           # uv dependencies
├── requirements-pipecat.txt # Python requirements
├── .env.pipecat            # Environment template
├── core/                   # Core agent building logic
├── knowledge/              # Knowledge base integration
└── generation/             # Code generation templates
```

## 🔑 **Required Environment Variables**

```bash
# Core AI Services (Required)
DEEPGRAM_API_KEY=your_deepgram_key
OPENAI_API_KEY=your_openai_key  
CARTESIA_API_KEY=your_cartesia_key

# Optional Services
ELEVENLABS_API_KEY=your_elevenlabs_key
ANTHROPIC_API_KEY=your_anthropic_key

# Agent Builder Settings
AGENT_BUILDER_NAME="Pipecat Agent Builder"
DEFAULT_VOICE_ID="71a7ad14-091c-4e8e-a314-022ece01c121"
LOG_LEVEL=INFO
```

## 🎨 **Customization**

### **Voice Personality**
Edit the system messages in `bot.py` to change the agent's personality:

```python
system_messages = [
    {
        "role": "system",
        "content": "You are a [PERSONALITY] AI assistant that helps users create voice agents..."
    }
]
```

### **Voice Selection**
Change the voice in `bot.py`:

```python
tts = CartesiaTTSService(
    api_key=os.getenv("CARTESIA_API_KEY"),
    voice_id="your_preferred_voice_id",  # Change this
)
```

### **Generation Templates**
Modify the code generation templates in `generation/` directory to customize the output agents.

## 📊 **Monitoring**

- **Pipecat Cloud Dashboard**: Monitor usage, performance, and costs
- **Logs**: View real-time logs in the dashboard
- **Metrics**: Track conversation success rates and generation quality

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Bot doesn't respond**:
   - Check API keys in Pipecat Cloud secrets
   - Verify microphone permissions in browser

2. **Poor voice quality**:
   - Check internet connection
   - Try different voice IDs in Cartesia

3. **Generation fails**:
   - Verify OpenAI API key has sufficient credits
   - Check conversation logs for errors

### **Debug Mode**

Set `LOG_LEVEL=DEBUG` in environment variables for detailed logging.

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `uv run bot.py`
5. Submit a pull request

## 📄 **License**

MIT License - see LICENSE file for details.

## 🆘 **Support**

- **Discord**: [Pipecat Community](https://discord.gg/pipecat)
- **Documentation**: [docs.pipecat.ai](https://docs.pipecat.ai)
- **GitHub Issues**: [Report bugs and feature requests](https://github.com/your-repo/issues)

---

**Built with ❤️ using [Pipecat](https://pipecat.ai) - The open-source framework for voice and multimodal AI agents.**
