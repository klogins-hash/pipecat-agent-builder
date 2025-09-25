"""Conversational interface for gathering agent requirements."""

import asyncio
import json
from typing import Dict, Any, List, Optional, AsyncGenerator
from enum import Enum
from dataclasses import dataclass, asdict

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask, PipelineParams
from pipecat.pipeline.runner import PipelineRunner
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.frames.frames import (
    Frame, TextFrame, LLMRunFrame, UserStartedSpeakingFrame, 
    UserStoppedSpeakingFrame, TranscriptionFrame
)
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.transports.network.small_webrtc import SmallWebRTCTransport, SmallWebRTCTransportParams

from core.config import AgentRequirements, AIServiceConfig, DeploymentConfig, KnowledgeSourceConfig, settings
from core.logger import setup_logger

logger = setup_logger("conversation_interface")


class ConversationState(Enum):
    """States of the requirements gathering conversation."""
    GREETING = "greeting"
    BASIC_INFO = "basic_info"
    USE_CASE = "use_case"
    CHANNELS = "channels"
    LANGUAGES = "languages"
    PERSONALITY = "personality"
    SERVICES = "services"
    KNOWLEDGE = "knowledge"
    INTEGRATIONS = "integrations"
    DEPLOYMENT = "deployment"
    CONFIRMATION = "confirmation"
    COMPLETE = "complete"


@dataclass
class ConversationProgress:
    """Track conversation progress and gathered information."""
    state: ConversationState = ConversationState.GREETING
    requirements: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.requirements is None:
            self.requirements = {
                "name": "",
                "description": "",
                "use_case": "",
                "channels": [],
                "languages": ["en"],
                "personality": "helpful and professional",
                "stt_service": None,
                "llm_service": None,
                "tts_service": None,
                "knowledge_sources": [],
                "integrations": [],
                "deployment": {}
            }


class RequirementsProcessor(FrameProcessor):
    """Process user input to extract agent requirements."""
    
    def __init__(self):
        super().__init__()
        self.progress = ConversationProgress()
        self.conversation_history = []
        
    async def process_frame(self, frame: Frame, direction: FrameDirection) -> AsyncGenerator[Frame, None]:
        """Process frames to extract requirements information."""
        
        # Pass through all frames
        yield frame
        
        # Process transcription frames to extract requirements
        if isinstance(frame, TranscriptionFrame) and direction == FrameDirection.DOWNSTREAM:
            await self._process_user_input(frame.text)
    
    async def _process_user_input(self, text: str):
        """Process user input based on current conversation state."""
        logger.info(f"Processing user input in state {self.progress.state}: {text}")
        
        # Store conversation history
        self.conversation_history.append({
            "state": self.progress.state.value,
            "user_input": text,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Extract information based on current state
        if self.progress.state == ConversationState.BASIC_INFO:
            await self._extract_basic_info(text)
        elif self.progress.state == ConversationState.USE_CASE:
            await self._extract_use_case(text)
        elif self.progress.state == ConversationState.CHANNELS:
            await self._extract_channels(text)
        elif self.progress.state == ConversationState.LANGUAGES:
            await self._extract_languages(text)
        elif self.progress.state == ConversationState.PERSONALITY:
            await self._extract_personality(text)
        elif self.progress.state == ConversationState.KNOWLEDGE:
            await self._extract_knowledge_sources(text)
        elif self.progress.state == ConversationState.INTEGRATIONS:
            await self._extract_integrations(text)
    
    async def _extract_basic_info(self, text: str):
        """Extract agent name and description."""
        # Simple keyword extraction - in production, use more sophisticated NLP
        text_lower = text.lower()
        
        # Try to extract agent name
        if "name" in text_lower or "call" in text_lower:
            # Extract quoted names or names after "call it" or "name it"
            import re
            name_patterns = [
                r'call it ["\']?([^"\']+)["\']?',
                r'name it ["\']?([^"\']+)["\']?',
                r'named? ["\']?([^"\']+)["\']?',
                r'["\']([^"\']+)["\']'
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    self.progress.requirements["name"] = match.group(1).strip()
                    break
        
        # Use the entire input as description if no specific name found
        if not self.progress.requirements["name"]:
            self.progress.requirements["name"] = "Custom Agent"
        
        self.progress.requirements["description"] = text
    
    async def _extract_use_case(self, text: str):
        """Extract use case information."""
        self.progress.requirements["use_case"] = text
    
    async def _extract_channels(self, text: str):
        """Extract supported channels."""
        text_lower = text.lower()
        channels = []
        
        if any(word in text_lower for word in ["phone", "call", "telephone", "dial"]):
            channels.append("phone")
        if any(word in text_lower for word in ["web", "website", "browser", "online"]):
            channels.append("web")
        if any(word in text_lower for word in ["mobile", "app", "ios", "android"]):
            channels.append("mobile")
        
        if not channels:
            # Default based on keywords
            if "customer service" in text_lower or "support" in text_lower:
                channels = ["phone", "web"]
            else:
                channels = ["web"]
        
        self.progress.requirements["channels"] = channels
    
    async def _extract_languages(self, text: str):
        """Extract supported languages."""
        text_lower = text.lower()
        languages = ["en"]  # Default to English
        
        language_map = {
            "spanish": "es",
            "french": "fr",
            "german": "de",
            "italian": "it",
            "portuguese": "pt",
            "chinese": "zh",
            "japanese": "ja",
            "korean": "ko",
            "russian": "ru",
            "arabic": "ar"
        }
        
        for lang_name, lang_code in language_map.items():
            if lang_name in text_lower:
                if lang_code not in languages:
                    languages.append(lang_code)
        
        self.progress.requirements["languages"] = languages
    
    async def _extract_personality(self, text: str):
        """Extract personality traits."""
        self.progress.requirements["personality"] = text
    
    async def _extract_knowledge_sources(self, text: str):
        """Extract knowledge source requirements."""
        text_lower = text.lower()
        sources = []
        
        # Detect different types of knowledge sources
        if any(word in text_lower for word in ["website", "url", "web", "scrape"]):
            # Extract URLs if present
            import re
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
            for url in urls:
                sources.append({
                    "type": "web",
                    "source": url,
                    "processing_options": {}
                })
        
        if any(word in text_lower for word in ["faq", "knowledge base", "documentation", "docs"]):
            sources.append({
                "type": "document",
                "source": "faq_database",
                "processing_options": {"format": "faq"}
            })
        
        if any(word in text_lower for word in ["api", "database", "system"]):
            sources.append({
                "type": "api",
                "source": "internal_api",
                "processing_options": {}
            })
        
        self.progress.requirements["knowledge_sources"] = sources
    
    async def _extract_integrations(self, text: str):
        """Extract integration requirements."""
        text_lower = text.lower()
        integrations = []
        
        integration_keywords = {
            "twilio": "twilio",
            "zendesk": "zendesk",
            "salesforce": "salesforce",
            "slack": "slack",
            "teams": "microsoft_teams",
            "discord": "discord",
            "whatsapp": "whatsapp",
            "telegram": "telegram"
        }
        
        for keyword, integration in integration_keywords.items():
            if keyword in text_lower:
                integrations.append(integration)
        
        self.progress.requirements["integrations"] = integrations
    
    def get_current_requirements(self) -> AgentRequirements:
        """Get current requirements as AgentRequirements object."""
        req_dict = self.progress.requirements.copy()
        
        # Convert knowledge sources to proper objects
        knowledge_sources = []
        for ks in req_dict.get("knowledge_sources", []):
            knowledge_sources.append(KnowledgeSourceConfig(**ks))
        req_dict["knowledge_sources"] = knowledge_sources
        
        # Set default deployment config
        if not req_dict.get("deployment"):
            req_dict["deployment"] = DeploymentConfig()
        else:
            req_dict["deployment"] = DeploymentConfig(**req_dict["deployment"])
        
        return AgentRequirements(**req_dict)


class ConversationOrchestrator:
    """Orchestrate the requirements gathering conversation."""
    
    def __init__(self):
        self.requirements_processor = RequirementsProcessor()
        self.transport = None
        self.task = None
        
    async def start_conversation(self) -> AgentRequirements:
        """Start the requirements gathering conversation."""
        logger.info("Starting agent requirements conversation")
        
        # Create services
        stt = DeepgramSTTService(api_key=settings.deepgram_api_key)
        llm = OpenAILLMService(
            api_key=settings.openai_api_key,
            model="gpt-4o"
        )
        tts = CartesiaTTSService(
            api_key=settings.cartesia_api_key,
            voice_id="71a7ad14-091c-4e8e-a314-022ece01c121"
        )
        
        # Create conversation context
        context = await self._create_conversation_context()
        context_aggregator = llm.create_context_aggregator(context)
        
        # Create transport
        self.transport = SmallWebRTCTransport(
            SmallWebRTCTransportParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
            )
        )
        
        # Create pipeline
        pipeline = Pipeline([
            self.transport.input(),
            stt,
            self.requirements_processor,
            context_aggregator.user(),
            llm,
            tts,
            self.transport.output(),
            context_aggregator.assistant(),
        ])
        
        # Create task
        self.task = PipelineTask(
            pipeline,
            params=PipelineParams(
                enable_metrics=True,
                enable_usage_metrics=True,
            ),
        )
        
        # Set up event handlers
        await self._setup_event_handlers()
        
        # Run the conversation
        runner = PipelineRunner()
        await runner.run(self.task)
        
        # Return gathered requirements
        return self.requirements_processor.get_current_requirements()
    
    async def _create_conversation_context(self) -> OpenAILLMContext:
        """Create the conversation context for requirements gathering."""
        
        system_message = """You are an expert Pipecat agent builder assistant. Your job is to have a natural conversation with the user to gather all the information needed to build their custom AI agent.

You should guide the conversation through these topics in order:
1. Basic information (agent name and description)
2. Use case (what the agent will do)
3. Channels (phone, web, mobile)
4. Languages (what languages to support)
5. Personality (how the agent should behave)
6. AI services (preferences for speech, language, and voice)
7. Knowledge sources (what information the agent needs access to)
8. Integrations (external systems to connect with)
9. Deployment preferences

Keep the conversation natural and engaging. Ask follow-up questions to clarify requirements. Once you have all the information, confirm the details with the user before proceeding to build the agent.

Start by greeting the user and asking them to describe what kind of AI agent they want to build."""
        
        messages = [{"role": "system", "content": system_message}]
        return OpenAILLMContext(messages)
    
    async def _setup_event_handlers(self):
        """Set up transport event handlers."""
        
        @self.transport.event_handler("on_client_connected")
        async def on_client_connected(transport, client):
            logger.info(f"Client connected for requirements gathering: {client}")
            await self.task.queue_frames([LLMRunFrame()])
        
        @self.transport.event_handler("on_client_disconnected")
        async def on_client_disconnected(transport, client):
            logger.info(f"Client disconnected: {client}")
            await self.task.cancel()


# Convenience function for external use
async def gather_agent_requirements() -> AgentRequirements:
    """Start a conversation to gather agent requirements."""
    orchestrator = ConversationOrchestrator()
    return await orchestrator.start_conversation()
