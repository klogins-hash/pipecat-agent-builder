# 🚀 Pipecat Agent Builder - Railway Deployment

**Build sophisticated voice AI agents through a beautiful web interface, deployed on Railway.**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

## ⚡ Quick Deploy to Railway

### 1. **One-Click Deploy**
Click the Railway button above or:
1. Fork this repository
2. Connect to Railway
3. Add environment variables
4. Deploy automatically

### 2. **Manual Deploy**
```bash
# Clone the repository
git clone https://github.com/yourusername/pipecat-agent-builder.git
cd pipecat-agent-builder

# Deploy to Railway
railway login
railway link
railway up
```

## 🔑 **Required Environment Variables**

### **Minimum Setup (3 keys needed):**
```bash
OPENAI_API_KEY=sk-proj-your-openai-key-here
DEEPGRAM_API_KEY=your-deepgram-key-here
CARTESIA_API_KEY=your-cartesia-key-here
```

### **Get Your API Keys:**
- **OpenAI:** https://platform.openai.com/api-keys
- **Deepgram:** https://console.deepgram.com/
- **Cartesia:** https://play.cartesia.ai/

### **Optional Keys (for advanced features):**
```bash
# Alternative AI providers
ELEVENLABS_API_KEY=your-elevenlabs-key
ANTHROPIC_API_KEY=your-anthropic-key

# Telephony (for phone agents)
DAILY_API_KEY=your-daily-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token

# Integrations
ZENDESK_API_TOKEN=your-zendesk-token
SLACK_BOT_TOKEN=xoxb-your-slack-token
```

## 🎯 **How It Works**

1. **Visit Your Railway App** - Beautiful web interface opens
2. **Describe Your Agent** - Fill out the simple form
3. **Click Build** - Agent generates in seconds
4. **Download & Deploy** - Get complete, runnable code

## 🏗️ **What You Get**

Each generated agent includes:
```
your-agent/
├── bot.py                  # Complete Pipecat agent
├── requirements.txt        # All dependencies
├── Dockerfile             # Container ready
├── pcc-deploy.toml        # Pipecat Cloud config
├── .env.example           # Environment template
└── knowledge_processor.py # AI knowledge integration
```

## 🚀 **Features**

- **🎨 Beautiful Web UI** - No coding required
- **⚡ Lightning Fast** - Agents ready in seconds
- **🧠 AI-Powered** - Uses 2,600+ Pipecat documentation chunks
- **🔧 Fully Customizable** - All major AI services supported
- **📱 Multi-Channel** - Web, phone, mobile support
- **🌍 Multi-Language** - English, Spanish, French, German+
- **☁️ Cloud Ready** - Deploy to Pipecat Cloud instantly

## 🛠️ **Supported AI Services**

### **Speech-to-Text (STT):**
- Deepgram (recommended)
- OpenAI Whisper

### **Large Language Models (LLM):**
- OpenAI GPT-4o (recommended)
- Anthropic Claude

### **Text-to-Speech (TTS):**
- Cartesia (recommended)
- ElevenLabs
- OpenAI TTS

### **Transport & Telephony:**
- Daily.co (WebRTC)
- Twilio (Phone/SMS)
- Telnyx (Alternative telephony)

## 📊 **Use Cases**

- **Customer Service Bots** - Handle support calls and chats
- **Sales Assistants** - Qualify leads and book meetings
- **Personal Assistants** - Schedule, remind, and organize
- **Educational Tutors** - Interactive learning experiences
- **Entertainment Bots** - Games, stories, and interactions

## 🔧 **Local Development**

```bash
# Clone and setup
git clone https://github.com/yourusername/pipecat-agent-builder.git
cd pipecat-agent-builder

# Install dependencies
pip install -r requirements-railway.txt

# Set environment variables
cp .env.railway .env
# Edit .env with your API keys

# Run locally
python web_app.py
```

Visit `http://localhost:8000` to use the web interface.

## 📚 **API Documentation**

### **Build Agent Endpoint**
```bash
POST /api/build-agent
Content-Type: application/json

{
  "name": "My Customer Bot",
  "description": "Handles customer inquiries",
  "use_case": "customer_service",
  "channels": ["web", "phone"],
  "languages": ["en", "es"],
  "personality": "professional and helpful"
}
```

### **Health Check**
```bash
GET /health
```

### **API Info**
```bash
GET /api/info
```

## 🐳 **Docker Deployment**

```bash
# Build image
docker build -t pipecat-agent-builder .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e DEEPGRAM_API_KEY=your-key \
  -e CARTESIA_API_KEY=your-key \
  pipecat-agent-builder
```

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **"Builder not initialized"**
   - Check Railway logs for startup errors
   - Verify environment variables are set

2. **"API key invalid"**
   - Verify API keys in Railway dashboard
   - Check key format and permissions

3. **"Build timeout"**
   - Railway has 10-minute build timeout
   - Check for large file uploads

### **Getting Help:**
- Check Railway logs: `railway logs`
- View health check: `https://your-app.railway.app/health`
- API status: `https://your-app.railway.app/api/info`

## 📈 **Performance**

- **Build Time:** ~0.3 seconds per agent
- **Memory Usage:** ~200MB base + vectorizer
- **Concurrent Users:** Scales with Railway plan
- **File Size:** ~50KB per generated agent

## 🔒 **Security**

- All API keys stored securely in Railway
- No sensitive data logged
- CORS configured for web safety
- Input validation on all endpoints

## 📄 **License**

MIT License - see LICENSE file for details.

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 🎉 **What's Next?**

After deployment:
1. **Test the web interface** - Build a sample agent
2. **Download and run** - Test locally with your API keys
3. **Deploy to production** - Use Pipecat Cloud or your infrastructure
4. **Scale up** - Add more AI services and integrations

---

**Ready to build voice AI agents in seconds?** 

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

**🚀 Deploy now and start building!**
