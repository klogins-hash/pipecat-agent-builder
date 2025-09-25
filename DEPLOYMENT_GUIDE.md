# 🚀 Railway Deployment Guide

## 📋 **Pre-Deployment Checklist**

### ✅ **Files Ready for Railway:**
- `Dockerfile` - Railway-optimized container
- `web_app.py` - FastAPI web interface  
- `requirements-railway.txt` - Web deployment dependencies
- `railway.json` - Railway configuration
- `.env.railway` - Complete environment template
- `README-RAILWAY.md` - Deployment documentation

### ✅ **Features Included:**
- Beautiful web interface for building agents
- API endpoints for programmatic access
- Health checks and monitoring
- Automatic file downloads
- Docker containerization
- Railway-specific optimizations

## 🔑 **Required API Keys (Minimum Setup)**

You need these 3 API keys for basic functionality:

```bash
OPENAI_API_KEY=sk-proj-your-openai-key-here
DEEPGRAM_API_KEY=your-deepgram-key-here  
CARTESIA_API_KEY=your-cartesia-key-here
```

### **Where to Get API Keys:**

1. **OpenAI** (for LLM): https://platform.openai.com/api-keys
   - Sign up → Create API key → Copy key starting with `sk-proj-`

2. **Deepgram** (for Speech-to-Text): https://console.deepgram.com/
   - Sign up → Create API key → Copy key

3. **Cartesia** (for Text-to-Speech): https://play.cartesia.ai/
   - Sign up → Get API key → Copy key

## 🚂 **Railway Deployment Steps**

### **Option 1: One-Click Deploy (Recommended)**
1. Push code to GitHub repository
2. Go to Railway.app
3. Click "Deploy from GitHub"
4. Select your repository
5. Add environment variables (see below)
6. Deploy automatically

### **Option 2: Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy from project directory
cd pipecat-agent-builder
railway up
```

### **Option 3: GitHub Integration**
1. Connect Railway to your GitHub account
2. Import the repository
3. Railway auto-detects Dockerfile
4. Set environment variables
5. Enable auto-deployments

## ⚙️ **Railway Environment Variables**

In Railway dashboard, add these environment variables:

### **Required (Minimum Setup):**
```
OPENAI_API_KEY = sk-proj-your-openai-key-here
DEEPGRAM_API_KEY = your-deepgram-key-here
CARTESIA_API_KEY = your-cartesia-key-here
```

### **Optional (Advanced Features):**
```
ELEVENLABS_API_KEY = your-elevenlabs-key-here
ANTHROPIC_API_KEY = your-anthropic-key-here
DAILY_API_KEY = your-daily-key-here
TWILIO_ACCOUNT_SID = your-twilio-sid-here
TWILIO_AUTH_TOKEN = your-twilio-token-here
```

### **Railway Auto-Set Variables:**
Railway automatically sets these - don't override:
- `PORT` - Application port
- `RAILWAY_ENVIRONMENT` - Environment name
- `RAILWAY_PROJECT_ID` - Project identifier

## 🔍 **Testing Your Deployment**

### **1. Health Check**
Visit: `https://your-app.railway.app/health`

Should return:
```json
{
  "status": "healthy",
  "builder_ready": true,
  "timestamp": 1234567890
}
```

### **2. Web Interface**
Visit: `https://your-app.railway.app`

Should show beautiful agent builder interface.

### **3. API Info**
Visit: `https://your-app.railway.app/api/info`

Should return API capabilities and status.

## 🎯 **Using Your Deployed App**

### **Web Interface:**
1. Visit your Railway app URL
2. Fill out the agent form
3. Click "Build My Agent"
4. Download the generated files
5. Deploy to your infrastructure

### **API Usage:**
```bash
curl -X POST https://your-app.railway.app/api/build-agent \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Test Bot",
    "description": "A simple test bot",
    "use_case": "customer_service",
    "channels": ["web"],
    "languages": ["en"]
  }'
```

## 📊 **Performance & Scaling**

### **Railway Plan Recommendations:**
- **Hobby Plan**: Perfect for testing and light usage
- **Pro Plan**: Recommended for production use
- **Team Plan**: For high-traffic applications

### **Expected Performance:**
- **Build Time**: ~0.3 seconds per agent
- **Memory Usage**: ~200MB base
- **Concurrent Users**: Scales with Railway plan
- **File Generation**: ~50KB per agent

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **Build Fails**
   ```bash
   # Check Railway logs
   railway logs
   
   # Common fixes:
   - Verify Dockerfile syntax
   - Check requirements-railway.txt
   - Ensure all files are committed
   ```

2. **App Won't Start**
   ```bash
   # Check environment variables
   - Verify API keys are set
   - Check for typos in variable names
   - Ensure PORT is not overridden
   ```

3. **API Errors**
   ```bash
   # Check API key validity
   - Test keys in provider dashboards
   - Verify key permissions
   - Check key format (sk-proj- for OpenAI)
   ```

### **Debug Commands:**
```bash
# View logs
railway logs

# Check environment
railway variables

# SSH into container (if needed)
railway shell
```

## 🚀 **Post-Deployment**

### **1. Test Agent Generation**
- Build a sample agent through web interface
- Download and verify files
- Test locally with your API keys

### **2. Monitor Usage**
- Check Railway metrics dashboard
- Monitor API key usage in provider dashboards
- Set up alerts for high usage

### **3. Scale as Needed**
- Upgrade Railway plan for more traffic
- Add more AI service providers
- Implement caching for better performance

## 📈 **Next Steps**

1. **Custom Domain**: Add your domain in Railway settings
2. **SSL Certificate**: Railway provides automatic HTTPS
3. **Monitoring**: Set up error tracking (Sentry)
4. **Analytics**: Add usage analytics (PostHog)
5. **Backup**: Regular backups of generated agents

## 🎉 **Success!**

Your Pipecat Agent Builder is now live on Railway! 

- **Web Interface**: Build agents through beautiful UI
- **API Access**: Programmatic agent generation
- **Auto-Scaling**: Handles traffic automatically
- **Global CDN**: Fast worldwide access

**Start building voice AI agents in seconds!** 🚀
