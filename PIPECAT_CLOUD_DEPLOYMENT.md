# 🚀 Pipecat Cloud Deployment Guide

## Step-by-Step Deployment Instructions

### **1. Prerequisites Setup**

**Sign up for services:**
- [Pipecat Cloud Account](https://pipecat.daily.co/sign-up)
- [Docker Hub Account](https://hub.docker.com/)
- [Deepgram API Key](https://console.deepgram.com/signup)
- [OpenAI API Key](https://auth.openai.com/create-account)
- [Cartesia API Key](https://play.cartesia.ai/sign-up)

**Install tools:**
```bash
# Install Docker
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### **2. Project Setup**

```bash
# Clone and setup
git clone <your-repo>
cd pipecat-agent-builder

# Create environment file
cp .env.pipecat .env

# Edit .env with your API keys
nano .env
```

**Required .env contents:**
```bash
DEEPGRAM_API_KEY=your_deepgram_key_here
OPENAI_API_KEY=your_openai_key_here
CARTESIA_API_KEY=your_cartesia_key_here
```

### **3. Local Testing**

```bash
# Install dependencies
uv sync

# Test locally
uv run bot.py
```

Visit http://localhost:7860 and test the voice interface.

### **4. Pipecat Cloud Deployment**

**Login to Pipecat Cloud:**
```bash
uv run pcc auth login
```

**Update deployment config:**
Edit `pcc-deploy.toml`:
```toml
agent_name = "agent-builder"
image = "YOUR_DOCKERHUB_USERNAME/pipecat-agent-builder:0.1"  # ← Update this
secret_set = "agent-builder-secrets"

[scaling]
	min_agents = 1
	max_agents = 5
```

**Upload secrets:**
```bash
uv run pcc secrets set agent-builder-secrets --file .env
```

**Build and deploy:**
```bash
# Build Docker image and push to Docker Hub
uv run pcc docker build-push

# Deploy to Pipecat Cloud
uv run pcc deploy
```

### **5. Access Your Agent**

1. Open [Pipecat Cloud Dashboard](https://pipecat.daily.co/)
2. Find your "agent-builder" agent
3. Click "Sandbox"
4. Allow microphone access
5. Click "Connect"
6. Start talking: "I want to build a customer service agent"

### **6. Monitoring**

- **Dashboard**: Monitor usage and performance
- **Logs**: View real-time conversation logs
- **Scaling**: Adjust min/max agents as needed

## 🎯 **Usage Examples**

Once deployed, users can say:

**"Create a restaurant reservation agent that can take bookings, answer menu questions, and handle special dietary requests. It should sound friendly and professional."**

**"Build a sales assistant for my SaaS company that qualifies leads, schedules demos, and integrates with HubSpot. Make it sound confident but not pushy."**

**"I need a customer support bot for my e-commerce store that can track orders, process returns, and escalate complex issues to humans."**

The agent will have natural conversations to gather requirements and generate complete Pipecat applications!

## 🔧 **Troubleshooting**

**Deployment fails:**
- Check Docker Hub credentials: `docker login`
- Verify API keys in secrets
- Check image name in pcc-deploy.toml

**Agent doesn't respond:**
- Check microphone permissions
- Verify API keys have credits
- Check Pipecat Cloud logs

**Poor voice quality:**
- Test internet connection
- Try different Cartesia voice IDs
- Check browser compatibility

## 📊 **Scaling**

Adjust scaling in `pcc-deploy.toml`:
```toml
[scaling]
	min_agents = 2    # Always ready instances
	max_agents = 10   # Peak capacity
```

Higher `min_agents` = faster response, higher cost
Higher `max_agents` = handle more concurrent users

## 🎉 **Success!**

Your voice-only Agent Builder is now live on Pipecat Cloud! Users can connect and build sophisticated voice AI agents through natural conversation.
