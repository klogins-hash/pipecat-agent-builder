"""Simplified conversation interface for testing purposes."""

import asyncio
from typing import Dict, Any

from core.config import AgentRequirements, AIServiceConfig, DeploymentConfig, KnowledgeSourceConfig
from core.logger import setup_logger

logger = setup_logger("simple_conversation")


async def gather_agent_requirements_simple() -> AgentRequirements:
    """Simplified requirements gathering for testing."""
    
    print("\n🤖 Pipecat Agent Builder - Requirements Gathering")
    print("=" * 50)
    print("Let's build your AI agent! I'll ask you a few questions.")
    print("(For testing, we'll use default values)")
    
    # For testing purposes, return a sample configuration
    # In production, this would be an interactive conversation
    
    requirements = AgentRequirements(
        name="Sample Customer Service Bot",
        description="A helpful customer service agent that can handle inquiries via phone and web",
        use_case="customer_service",
        channels=["web", "phone"],
        languages=["en", "es"],
        personality="professional, empathetic, and solution-oriented",
        stt_service=AIServiceConfig(
            name="deepgram",
            provider="deepgram",
            model="nova-2"
        ),
        llm_service=AIServiceConfig(
            name="openai",
            provider="openai",
            model="gpt-4o"
        ),
        tts_service=AIServiceConfig(
            name="cartesia",
            provider="cartesia",
            voice_id="71a7ad14-091c-4e8e-a314-022ece01c121"
        ),
        knowledge_sources=[
            KnowledgeSourceConfig(
                type="web",
                source="https://help.company.com",
                processing_options={"crawl_depth": 2}
            ),
            KnowledgeSourceConfig(
                type="document",
                source="faq_database.pdf",
                processing_options={"format": "faq"}
            )
        ],
        integrations=["zendesk", "twilio"],
        deployment=DeploymentConfig(
            platform="pipecat-cloud",
            scaling_min=2,
            scaling_max=10,
            region="us-west-2"
        )
    )
    
    print(f"\n✅ Requirements gathered for: {requirements.name}")
    print(f"   Use case: {requirements.use_case}")
    print(f"   Channels: {', '.join(requirements.channels)}")
    print(f"   Languages: {', '.join(requirements.languages)}")
    print(f"   Knowledge sources: {len(requirements.knowledge_sources)}")
    print(f"   Integrations: {', '.join(requirements.integrations)}")
    
    return requirements
