#!/usr/bin/env python3
"""
Example usage of Pipecat Agent Builder programmatic API.

This demonstrates how to use the system programmatically instead of 
through the conversational interface.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import AgentRequirements, AIServiceConfig, DeploymentConfig, KnowledgeSourceConfig
from core.logger import setup_logger
from knowledge.vectorizer import PipecatDocumentationVectorizer
from generation.templates import PipecatTemplateGenerator
from mcp.cascade_client import CascadeOrchestrator
from deployment.pipecat_cloud import PipecatCloudDeployer

logger = setup_logger("example_usage")


async def example_customer_service_bot():
    """Example: Build a customer service bot programmatically."""
    
    logger.info("Building customer service bot example...")
    
    # Define agent requirements
    requirements = AgentRequirements(
        name="Customer Service Assistant",
        description="A helpful customer service agent that can handle inquiries, access FAQ database, and escalate to human agents when needed.",
        use_case="customer_service",
        channels=["phone", "web"],
        languages=["en", "es"],
        personality="professional, empathetic, and solution-oriented",
        
        # AI service preferences
        stt_service=AIServiceConfig(
            name="deepgram",
            provider="deepgram",
            model="nova-2",
            language="en"
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
        
        # Knowledge sources
        knowledge_sources=[
            KnowledgeSourceConfig(
                type="web",
                source="https://help.yourcompany.com",
                processing_options={"crawl_depth": 2}
            ),
            KnowledgeSourceConfig(
                type="document",
                source="faq_database.pdf",
                processing_options={"format": "faq"}
            )
        ],
        
        # Integrations
        integrations=["zendesk", "twilio"],
        
        # Deployment configuration
        deployment=DeploymentConfig(
            platform="pipecat-cloud",
            scaling_min=2,
            scaling_max=10,
            region="us-west-2",
            environment="production"
        )
    )
    
    return requirements


async def example_personal_assistant():
    """Example: Build a personal assistant bot."""
    
    logger.info("Building personal assistant example...")
    
    requirements = AgentRequirements(
        name="Personal AI Assistant",
        description="A smart personal assistant that helps with scheduling, answers questions, and manages daily tasks.",
        use_case="personal_assistant",
        channels=["web", "mobile"],
        languages=["en"],
        personality="friendly, proactive, and organized",
        
        # High-quality services for personal use
        stt_service=AIServiceConfig(
            name="openai",
            provider="openai",
            model="whisper-1"
        ),
        llm_service=AIServiceConfig(
            name="openai",
            provider="openai",
            model="gpt-4o"
        ),
        tts_service=AIServiceConfig(
            name="elevenlabs",
            provider="elevenlabs",
            voice_id="pNInz6obpgDQGcFmaJgB"  # Premium voice
        ),
        
        # Personal knowledge sources
        knowledge_sources=[
            KnowledgeSourceConfig(
                type="document",
                source="personal_notes.md",
                processing_options={"format": "markdown"}
            ),
            KnowledgeSourceConfig(
                type="api",
                source="calendar_api",
                processing_options={"endpoint": "https://api.calendar.com/v1"}
            )
        ],
        
        # Personal integrations
        integrations=["google_calendar", "slack", "notion"],
        
        deployment=DeploymentConfig(
            scaling_min=1,
            scaling_max=3,
            environment="development"
        )
    )
    
    return requirements


async def example_educational_tutor():
    """Example: Build an educational tutor bot."""
    
    logger.info("Building educational tutor example...")
    
    requirements = AgentRequirements(
        name="Math Tutor AI",
        description="An intelligent math tutor that helps students learn algebra, geometry, and calculus with personalized explanations.",
        use_case="education",
        channels=["web"],
        languages=["en", "es", "fr"],
        personality="patient, encouraging, and pedagogical",
        
        # Education-optimized services
        stt_service=AIServiceConfig(
            name="deepgram",
            provider="deepgram",
            model="nova-2"
        ),
        llm_service=AIServiceConfig(
            name="anthropic",
            provider="anthropic",
            model="claude-3-sonnet-20240229"  # Good for educational content
        ),
        tts_service=AIServiceConfig(
            name="cartesia",
            provider="cartesia",
            voice_id="teacher_voice_id"
        ),
        
        # Educational knowledge sources
        knowledge_sources=[
            KnowledgeSourceConfig(
                type="web",
                source="https://www.khanacademy.org/math",
                processing_options={"subject": "mathematics"}
            ),
            KnowledgeSourceConfig(
                type="document",
                source="math_curriculum.pdf",
                processing_options={"format": "educational"}
            )
        ],
        
        integrations=["khan_academy", "wolfram_alpha"],
        
        deployment=DeploymentConfig(
            scaling_min=1,
            scaling_max=5,
            region="us-east-1"
        )
    )
    
    return requirements


async def build_agent_programmatically(requirements: AgentRequirements):
    """Build an agent using the programmatic API."""
    
    logger.info(f"Building agent: {requirements.name}")
    
    # Step 1: Initialize components
    vectorizer = PipecatDocumentationVectorizer()
    template_generator = PipecatTemplateGenerator()
    deployer = PipecatCloudDeployer()
    
    # Step 2: Get knowledge context
    logger.info("Searching knowledge base...")
    knowledge_context = []
    
    # Search for relevant patterns
    search_queries = [
        f"{requirements.use_case} pipecat example",
        f"pipecat {' '.join(requirements.channels)} transport",
        f"{requirements.stt_service.provider} speech to text",
        f"{requirements.llm_service.provider} language model",
        f"{requirements.tts_service.provider} text to speech"
    ]
    
    for query in search_queries:
        results = await vectorizer.search(query, n_results=2)
        knowledge_context.extend(results)
    
    logger.info(f"Found {len(knowledge_context)} relevant knowledge chunks")
    
    # Step 3: Generate code
    logger.info("Generating agent code...")
    
    # Try Windsurf Cascade first, fall back to templates
    generated_files = {}
    try:
        async with CascadeOrchestrator() as cascade:
            logger.info("Using Windsurf Cascade for advanced generation...")
            result = await cascade.build_complete_agent(requirements, knowledge_context)
            generated_files = result.get("agent_code", {}).get("code_files", {})
    except Exception as e:
        logger.warning(f"Cascade unavailable, using templates: {e}")
        generated_files = template_generator.generate_agent_files(requirements)
    
    # Step 4: Save files
    logger.info("Saving generated files...")
    agent_name = requirements.name.lower().replace(' ', '_')
    output_dir = Path("generated_agents") / agent_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for filename, content in generated_files.items():
        file_path = output_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    logger.info(f"Agent saved to: {output_dir}")
    
    # Step 5: Optional deployment
    deploy_choice = input(f"\nDeploy {requirements.name} to Pipecat Cloud? (y/n): ").lower().strip()
    if deploy_choice == 'y':
        logger.info("Deploying to Pipecat Cloud...")
        try:
            deployment_result = await deployer.deploy_agent(requirements, output_dir)
            logger.info(f"Deployment result: {deployment_result}")
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
    
    return output_dir


async def main():
    """Main example function."""
    
    print("🤖 Pipecat Agent Builder - Programmatic Examples")
    print("=" * 50)
    
    examples = {
        "1": ("Customer Service Bot", example_customer_service_bot),
        "2": ("Personal Assistant", example_personal_assistant),
        "3": ("Educational Tutor", example_educational_tutor),
    }
    
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    choice = input("\nSelect example (1-3) or 'all' to build all: ").strip()
    
    if choice == "all":
        # Build all examples
        for name, example_func in examples.values():
            print(f"\n🏗️  Building {name}...")
            requirements = await example_func()
            await build_agent_programmatically(requirements)
    elif choice in examples:
        # Build selected example
        name, example_func = examples[choice]
        print(f"\n🏗️  Building {name}...")
        requirements = await example_func()
        await build_agent_programmatically(requirements)
    else:
        print("Invalid choice. Exiting.")
        return
    
    print("\n🎉 Example completed!")
    print("\nNext steps:")
    print("1. Check the generated_agents/ directory")
    print("2. Review the generated code")
    print("3. Test locally: cd generated_agents/agent_name && python bot.py")
    print("4. Deploy: pcc deploy")


if __name__ == "__main__":
    asyncio.run(main())
