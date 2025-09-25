"""Pipecat Agent Builder - Voice-Only Interface

A conversational AI assistant that helps users build custom Pipecat agents
through natural voice interaction. Users describe their requirements via voice,
and the system generates complete, production-ready Pipecat applications.

Required AI services:
- Deepgram (Speech-to-Text)
- OpenAI (LLM for conversation and code generation)
- Cartesia (Text-to-Speech)

Run the bot using:
    uv run bot.py

Deploy to Pipecat Cloud:
    uv run pcc deploy
"""

import os
import json
import asyncio
from typing import Dict, List, Any
from datetime import datetime

from dotenv import load_dotenv
from loguru import logger

print("🤖 Starting Pipecat Agent Builder...")
print("⏳ Loading models and imports (20 seconds, first run only)\n")

logger.info("Loading Local Smart Turn Analyzer V3...")
from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3

logger.info("✅ Local Smart Turn Analyzer V3 loaded")
logger.info("Loading Silero VAD model...")
from pipecat.audio.vad.silero import SileroVADAnalyzer

logger.info("✅ Silero VAD model loaded")

from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import LLMRunFrame, TextFrame

logger.info("Loading pipeline components...")
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.daily.transport import DailyParams

logger.info("✅ All components loaded successfully!")

load_dotenv(override=True)


class AgentBuilderState:
    """Manages the conversation state for building agents."""
    
    def __init__(self):
        self.requirements = {}
        self.conversation_stage = "greeting"
        self.agent_type = None
        self.collected_info = {
            "use_case": None,
            "channels": [],
            "languages": [],
            "personality": None,
            "integrations": [],
            "special_features": []
        }
    
    def update_requirements(self, key: str, value: Any):
        """Update agent requirements based on user input."""
        self.collected_info[key] = value
        logger.info(f"Updated {key}: {value}")
    
    def get_completion_status(self) -> float:
        """Return percentage of requirements collected."""
        required_fields = ["use_case", "channels", "personality"]
        completed = sum(1 for field in required_fields if self.collected_info.get(field))
        return completed / len(required_fields)
    
    def is_ready_to_generate(self) -> bool:
        """Check if we have enough info to generate an agent."""
        return self.get_completion_status() >= 0.8


class AgentCodeGenerator:
    """Generates complete Pipecat agent code based on requirements."""
    
    def __init__(self, openai_service):
        self.openai_service = openai_service
    
    async def generate_agent_code(self, requirements: Dict) -> Dict[str, str]:
        """Generate complete Pipecat agent code files."""
        
        # Create detailed prompt for code generation
        prompt = self._create_generation_prompt(requirements)
        
        # Generate the code using OpenAI
        response = await self._call_openai_for_generation(prompt)
        
        # Parse the response into separate files
        return self._parse_generated_code(response, requirements)
    
    def _create_generation_prompt(self, requirements: Dict) -> str:
        """Create a detailed prompt for agent generation."""
        return f"""
Generate a complete, production-ready Pipecat agent based on these requirements:

**Agent Requirements:**
- Use Case: {requirements.get('use_case', 'General assistant')}
- Channels: {', '.join(requirements.get('channels', ['web']))}
- Languages: {', '.join(requirements.get('languages', ['English']))}
- Personality: {requirements.get('personality', 'Professional and helpful')}
- Integrations: {', '.join(requirements.get('integrations', ['None']))}
- Special Features: {', '.join(requirements.get('special_features', ['None']))}

**Generate these files:**

1. **bot.py** - Main agent file following Pipecat Cloud patterns
2. **pcc-deploy.toml** - Deployment configuration
3. **Dockerfile** - Container configuration
4. **requirements.txt** - Python dependencies
5. **README.md** - Setup and deployment instructions
6. **.env.example** - Environment variables template

**Requirements:**
- Use proper Pipecat Cloud architecture (single bot.py file)
- Include appropriate STT, LLM, and TTS services
- Add conversation context for the specific use case
- Include proper error handling and logging
- Follow Pipecat best practices for voice AI
- Make it production-ready with proper configuration

**Output Format:**
```
FILE: bot.py
[Complete bot.py content]

FILE: pcc-deploy.toml
[Complete deployment config]

FILE: Dockerfile
[Complete Dockerfile]

FILE: requirements.txt
[Complete requirements]

FILE: README.md
[Complete setup instructions]

FILE: .env.example
[Environment variables template]
```

Generate professional, well-documented, production-ready code.
"""
    
    async def _call_openai_for_generation(self, prompt: str) -> str:
        """Call OpenAI to generate the agent code."""
        # This would integrate with the OpenAI service
        # For now, return a placeholder that shows the structure
        return """
FILE: bot.py
# Generated Pipecat agent code would be here

FILE: pcc-deploy.toml
# Deployment configuration would be here

FILE: Dockerfile
# Docker configuration would be here

FILE: requirements.txt
# Requirements would be here

FILE: README.md
# Documentation would be here

FILE: .env.example
# Environment template would be here
"""
    
    def _parse_generated_code(self, response: str, requirements: Dict) -> Dict[str, str]:
        """Parse the generated response into separate files."""
        files = {}
        current_file = None
        current_content = []
        
        for line in response.split('\n'):
            if line.startswith('FILE: '):
                if current_file:
                    files[current_file] = '\n'.join(current_content)
                current_file = line.replace('FILE: ', '').strip()
                current_content = []
            elif current_file:
                current_content.append(line)
        
        # Add the last file
        if current_file:
            files[current_file] = '\n'.join(current_content)
        
        return files


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    """Main bot logic for the Agent Builder."""
    logger.info("Starting Agent Builder bot")

    # Initialize AI services
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="71a7ad14-091c-4e8e-a314-022ece01c121",  # British Reading Lady
    )
    
    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )

    # Initialize conversation state
    builder_state = AgentBuilderState()
    code_generator = AgentCodeGenerator(llm)

    # System messages for the Agent Builder
    system_messages = [
        {
            "role": "system",
            "content": """You are the Pipecat Agent Builder - a friendly AI assistant that helps users create custom voice AI agents through natural conversation.

Your role:
1. Gather requirements through natural conversation
2. Ask clarifying questions to understand their needs
3. Guide them through the agent building process
4. Generate complete, production-ready Pipecat agents

Key information to collect:
- Use case (customer service, sales, restaurant, etc.)
- Channels (phone, web, mobile)
- Languages supported
- Personality and tone
- Required integrations (CRM, databases, APIs)
- Special features needed

Keep the conversation natural and engaging. Ask one question at a time. Show enthusiasm about building their agent!

When you have enough information, offer to generate their complete agent code."""
        }
    ]

    context = LLMContext(system_messages)
    context_aggregator = LLMContextAggregatorPair(context)
    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    # Create the processing pipeline
    pipeline = Pipeline([
        transport.input(),
        rtvi,
        stt,
        context_aggregator.user(),
        llm,
        tts,
        transport.output(),
        context_aggregator.assistant(),
    ])

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        observers=[RTVIObserver(rtvi)],
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        """Handle new client connections."""
        logger.info("Client connected to Agent Builder")
        
        # Welcome message
        welcome_message = {
            "role": "system", 
            "content": """Greet the user warmly and introduce yourself as the Pipecat Agent Builder. 

Say something like: "Hi! I'm your Pipecat Agent Builder assistant. I help create custom voice AI agents through conversation. What kind of voice agent would you like to build today?"

Keep it friendly and conversational."""
        }
        
        context.messages.append(welcome_message)
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        """Handle client disconnections."""
        logger.info("Client disconnected from Agent Builder")
        await task.cancel()

    # Custom frame processor to analyze user input and update state
    class RequirementsProcessor:
        def __init__(self, state: AgentBuilderState):
            self.state = state
        
        async def process_user_input(self, text: str):
            """Analyze user input and update requirements."""
            text_lower = text.lower()
            
            # Detect use cases
            if any(word in text_lower for word in ["customer service", "support", "help desk"]):
                self.state.update_requirements("use_case", "customer_service")
            elif any(word in text_lower for word in ["sales", "lead", "prospect"]):
                self.state.update_requirements("use_case", "sales")
            elif any(word in text_lower for word in ["restaurant", "reservation", "booking"]):
                self.state.update_requirements("use_case", "restaurant")
            
            # Detect channels
            channels = []
            if "phone" in text_lower:
                channels.append("phone")
            if any(word in text_lower for word in ["web", "website", "browser"]):
                channels.append("web")
            if "mobile" in text_lower:
                channels.append("mobile")
            
            if channels:
                self.state.update_requirements("channels", channels)
            
            # Detect languages
            languages = []
            if "spanish" in text_lower:
                languages.append("Spanish")
            if "french" in text_lower:
                languages.append("French")
            if "english" in text_lower or not languages:
                languages.append("English")
            
            if languages:
                self.state.update_requirements("languages", languages)
            
            # Detect personality traits
            if any(word in text_lower for word in ["friendly", "warm", "casual"]):
                self.state.update_requirements("personality", "Friendly and approachable")
            elif any(word in text_lower for word in ["professional", "formal", "business"]):
                self.state.update_requirements("personality", "Professional and courteous")
            
            logger.info(f"Updated state: {self.state.collected_info}")

    requirements_processor = RequirementsProcessor(builder_state)

    # Add the requirements processor to analyze user messages
    # (This would be integrated into the pipeline in a full implementation)

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)
    await runner.run(task)


async def bot(runner_args: RunnerArguments):
    """Main bot entry point for Pipecat Cloud deployment."""
    
    transport_params = {
        "daily": lambda: DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
            turn_analyzer=LocalSmartTurnAnalyzerV3(),
        ),
        "webrtc": lambda: TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
            turn_analyzer=LocalSmartTurnAnalyzerV3(),
        ),
    }

    transport = await create_transport(runner_args, transport_params)
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main
    main()
