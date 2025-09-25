#!/usr/bin/env python3
"""
Pipecat Agent Builder - Web Interface for Railway Deployment
"""

import os
import asyncio
import json
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our MVP components
from mvp_main import SimplePipecatAgentBuilder
from core.simple_config import AgentRequirements, AIServiceConfig, KnowledgeSourceConfig, DeploymentConfig

# Initialize FastAPI app
app = FastAPI(
    title="Pipecat Agent Builder",
    description="Build voice AI agents with natural language",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global builder instance
builder = None

# Request/Response models
class AgentRequest(BaseModel):
    name: str
    description: str
    use_case: str
    channels: list[str] = ["web"]
    languages: list[str] = ["en"]
    personality: str = "helpful and professional"
    
    # Optional AI services
    stt_provider: str = "deepgram"
    llm_provider: str = "openai"
    tts_provider: str = "cartesia"
    
    # Optional knowledge sources
    knowledge_sources: list[dict] = []
    integrations: list[str] = []

class AgentResponse(BaseModel):
    success: bool
    agent_name: str
    agent_id: str
    download_url: str
    files_generated: list[str]
    message: str

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the agent builder on startup."""
    global builder
    try:
        builder = SimplePipecatAgentBuilder()
        await builder.initialize()
        print("🚀 Pipecat Agent Builder initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize builder: {e}")
        builder = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway."""
    return {
        "status": "healthy",
        "builder_ready": builder is not None,
        "timestamp": asyncio.get_event_loop().time()
    }

# Main web interface
@app.get("/", response_class=HTMLResponse)
async def get_web_interface():
    """Serve the main web interface."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pipecat Agent Builder</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white; 
            padding: 40px 30px; 
            text-align: center; 
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.1em; }
        .form-container { padding: 40px 30px; }
        .form-group { margin-bottom: 25px; }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 600; 
            color: #374151;
        }
        input, textarea, select { 
            width: 100%; 
            padding: 12px 16px; 
            border: 2px solid #e5e7eb; 
            border-radius: 10px; 
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus, select:focus { 
            outline: none; 
            border-color: #4f46e5; 
        }
        textarea { resize: vertical; min-height: 100px; }
        .checkbox-group { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
            gap: 10px; 
            margin-top: 10px;
        }
        .checkbox-item { 
            display: flex; 
            align-items: center; 
            padding: 8px 12px; 
            border: 2px solid #e5e7eb; 
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .checkbox-item:hover { border-color: #4f46e5; background: #f8fafc; }
        .checkbox-item input { width: auto; margin-right: 8px; }
        .submit-btn { 
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white; 
            padding: 16px 32px; 
            border: none; 
            border-radius: 10px; 
            font-size: 18px; 
            font-weight: 600;
            cursor: pointer; 
            width: 100%;
            transition: transform 0.3s;
        }
        .submit-btn:hover { transform: translateY(-2px); }
        .submit-btn:disabled { 
            opacity: 0.6; 
            cursor: not-allowed; 
            transform: none;
        }
        .loading { 
            display: none; 
            text-align: center; 
            padding: 20px;
        }
        .spinner { 
            border: 4px solid #f3f4f6; 
            border-top: 4px solid #4f46e5; 
            border-radius: 50%; 
            width: 40px; 
            height: 40px; 
            animation: spin 1s linear infinite; 
            margin: 0 auto 20px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .result { 
            display: none; 
            background: #f0fdf4; 
            border: 2px solid #22c55e; 
            border-radius: 10px; 
            padding: 20px; 
            margin-top: 20px;
        }
        .download-btn { 
            background: #22c55e; 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 8px; 
            text-decoration: none; 
            display: inline-block; 
            margin-top: 15px;
            font-weight: 600;
        }
        .error { 
            display: none; 
            background: #fef2f2; 
            border: 2px solid #ef4444; 
            border-radius: 10px; 
            padding: 20px; 
            margin-top: 20px; 
            color: #dc2626;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Pipecat Agent Builder</h1>
            <p>Build sophisticated voice AI agents in seconds</p>
        </div>
        
        <div class="form-container">
            <form id="agentForm">
                <div class="form-group">
                    <label for="name">Agent Name *</label>
                    <input type="text" id="name" name="name" required placeholder="e.g., Customer Service Bot">
                </div>
                
                <div class="form-group">
                    <label for="description">Description *</label>
                    <textarea id="description" name="description" required placeholder="Describe what your agent does..."></textarea>
                </div>
                
                <div class="form-group">
                    <label for="use_case">Use Case *</label>
                    <select id="use_case" name="use_case" required>
                        <option value="">Select a use case</option>
                        <option value="customer_service">Customer Service</option>
                        <option value="sales_assistant">Sales Assistant</option>
                        <option value="personal_assistant">Personal Assistant</option>
                        <option value="support_bot">Support Bot</option>
                        <option value="educational">Educational</option>
                        <option value="entertainment">Entertainment</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Channels</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" id="web" name="channels" value="web" checked>
                            <label for="web">Web</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="phone" name="channels" value="phone">
                            <label for="phone">Phone</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="mobile" name="channels" value="mobile">
                            <label for="mobile">Mobile</label>
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Languages</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" id="en" name="languages" value="en" checked>
                            <label for="en">English</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="es" name="languages" value="es">
                            <label for="es">Spanish</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="fr" name="languages" value="fr">
                            <label for="fr">French</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="de" name="languages" value="de">
                            <label for="de">German</label>
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="personality">Personality</label>
                    <input type="text" id="personality" name="personality" placeholder="e.g., professional, friendly, empathetic" value="helpful and professional">
                </div>
                
                <button type="submit" class="submit-btn" id="submitBtn">
                    🚀 Build My Agent
                </button>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Building your agent... This may take a few moments.</p>
            </div>
            
            <div class="result" id="result">
                <h3>🎉 Agent Built Successfully!</h3>
                <p id="resultMessage"></p>
                <a href="#" id="downloadBtn" class="download-btn">📥 Download Agent Files</a>
            </div>
            
            <div class="error" id="error">
                <h3>❌ Error</h3>
                <p id="errorMessage"></p>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('agentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const form = e.target;
            const formData = new FormData(form);
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            document.getElementById('error').style.display = 'none';
            document.getElementById('submitBtn').disabled = true;
            
            // Collect form data
            const channels = Array.from(form.querySelectorAll('input[name="channels"]:checked')).map(cb => cb.value);
            const languages = Array.from(form.querySelectorAll('input[name="languages"]:checked')).map(cb => cb.value);
            
            const agentData = {
                name: formData.get('name'),
                description: formData.get('description'),
                use_case: formData.get('use_case'),
                channels: channels,
                languages: languages,
                personality: formData.get('personality') || 'helpful and professional'
            };
            
            try {
                const response = await fetch('/api/build-agent', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(agentData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('resultMessage').textContent = result.message;
                    document.getElementById('downloadBtn').href = result.download_url;
                    document.getElementById('result').style.display = 'block';
                } else {
                    throw new Error(result.message || 'Unknown error occurred');
                }
            } catch (error) {
                document.getElementById('errorMessage').textContent = error.message;
                document.getElementById('error').style.display = 'block';
            } finally {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('submitBtn').disabled = false;
            }
        });
    </script>
</body>
</html>
    """

# API endpoint to build agent
@app.post("/api/build-agent", response_model=AgentResponse)
async def build_agent(request: AgentRequest, background_tasks: BackgroundTasks):
    """Build a Pipecat agent from the request."""
    
    if not builder:
        raise HTTPException(status_code=503, detail="Agent builder not initialized")
    
    try:
        # Convert request to AgentRequirements
        requirements = AgentRequirements(
            name=request.name,
            description=request.description,
            use_case=request.use_case,
            channels=request.channels,
            languages=request.languages,
            personality=request.personality,
            stt_service=AIServiceConfig(name=request.stt_provider, provider=request.stt_provider),
            llm_service=AIServiceConfig(name=request.llm_provider, provider=request.llm_provider),
            tts_service=AIServiceConfig(name=request.tts_provider, provider=request.tts_provider),
            knowledge_sources=[KnowledgeSourceConfig(**ks) for ks in request.knowledge_sources],
            integrations=request.integrations
        )
        
        # Build the agent
        result = await builder.build_agent(requirements)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail="Agent building failed")
        
        # Create agent ID and zip file
        agent_id = result["agent_directory"].split("/")[-1]
        zip_path = await create_agent_zip(result["agent_directory"], agent_id)
        
        return AgentResponse(
            success=True,
            agent_name=result["agent_name"],
            agent_id=agent_id,
            download_url=f"/download/{agent_id}",
            files_generated=result["files_generated"],
            message=f"Agent '{result['agent_name']}' built successfully! {len(result['files_generated'])} files generated."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Download endpoint
@app.get("/download/{agent_id}")
async def download_agent(agent_id: str):
    """Download the agent zip file."""
    zip_path = Path(f"/tmp/agent_{agent_id}.zip")
    
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Agent files not found")
    
    return FileResponse(
        path=zip_path,
        filename=f"{agent_id}.zip",
        media_type="application/zip"
    )

# Helper function to create zip file
async def create_agent_zip(agent_directory: str, agent_id: str) -> str:
    """Create a zip file of the agent directory."""
    agent_path = Path(agent_directory)
    zip_path = Path(f"/tmp/agent_{agent_id}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in agent_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(agent_path)
                zipf.write(file_path, arcname)
    
    return str(zip_path)

# API info endpoint
@app.get("/api/info")
async def get_api_info():
    """Get API information."""
    return {
        "name": "Pipecat Agent Builder API",
        "version": "1.0.0",
        "description": "Build voice AI agents with natural language",
        "builder_ready": builder is not None,
        "supported_channels": ["web", "phone", "mobile"],
        "supported_languages": ["en", "es", "fr", "de", "it", "pt", "zh", "ja"],
        "supported_providers": {
            "stt": ["deepgram", "openai"],
            "llm": ["openai", "anthropic"],
            "tts": ["cartesia", "elevenlabs", "openai"]
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
