#!/usr/bin/env python3
"""
Pipecat Agent Builder - MVP Version

Simplified version focused on core functionality:
- Requirements gathering (programmatic)
- Code generation (templates)
- Basic deployment
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

# Use simplified config
from core.simple_config import AgentRequirements, AIServiceConfig, KnowledgeSourceConfig, settings
from core.logger import setup_logger
from knowledge.vectorizer import PipecatDocumentationVectorizer
from generation.templates import PipecatTemplateGenerator

logger = setup_logger("mvp_main")


class SimplePipecatAgentBuilder:
    """Simplified Pipecat Agent Builder for MVP testing."""
    
    def __init__(self):
        self.vectorizer = None
        self.template_generator = PipecatTemplateGenerator()
        
    async def initialize(self):
        """Initialize the builder components."""
        logger.info("Initializing Pipecat Agent Builder MVP...")
        
        # Initialize vectorizer (optional - graceful fallback)
        try:
            self.vectorizer = PipecatDocumentationVectorizer()
            logger.info("✅ Vectorizer initialized")
        except Exception as e:
            logger.warning(f"⚠️  Vectorizer not available: {e}")
            self.vectorizer = None
        
        logger.info("🚀 MVP Builder ready!")
    
    async def build_agent(self, requirements: AgentRequirements) -> Dict[str, Any]:
        """Build an agent from requirements - simplified flow."""
        
        logger.info(f"🏗️  Building agent: {requirements.name}")
        
        # Step 1: Get knowledge context (optional)
        knowledge_context = []
        if self.vectorizer:
            try:
                knowledge_context = await self._get_knowledge_context(requirements)
                logger.info(f"📚 Found {len(knowledge_context)} knowledge chunks")
            except Exception as e:
                logger.warning(f"⚠️  Knowledge search failed: {e}")
        
        # Step 2: Generate code (core functionality)
        try:
            generated_files = self.template_generator.generate_agent_files(requirements)
            logger.info(f"✅ Generated {len(generated_files)} files")
        except Exception as e:
            logger.error(f"❌ Code generation failed: {e}")
            raise
        
        # Step 3: Save files
        try:
            agent_dir = await self._save_files(requirements, generated_files)
            logger.info(f"💾 Agent saved to: {agent_dir}")
        except Exception as e:
            logger.error(f"❌ File saving failed: {e}")
            raise
        
        # Return build result
        return {
            "success": True,
            "agent_name": requirements.name,
            "agent_directory": str(agent_dir),
            "files_generated": list(generated_files.keys()),
            "knowledge_chunks": len(knowledge_context)
        }
    
    async def _get_knowledge_context(self, requirements: AgentRequirements) -> list:
        """Get relevant knowledge context."""
        if not self.vectorizer:
            return []
        
        # Simple search queries based on requirements
        queries = [
            f"{requirements.use_case} agent example",
            f"pipecat {' '.join(requirements.channels)} setup",
            "basic agent configuration"
        ]
        
        knowledge_context = []
        for query in queries:
            try:
                results = await self.vectorizer.search(query, n_results=2)
                knowledge_context.extend(results)
            except Exception as e:
                logger.warning(f"Search failed for '{query}': {e}")
        
        return knowledge_context
    
    async def _save_files(self, requirements: AgentRequirements, generated_files: dict) -> Path:
        """Save generated files to disk."""
        # Create agent directory
        agent_name = requirements.name.lower().replace(' ', '_').replace('-', '_')
        agent_dir = Path(settings.output_path) / agent_name
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        # Save all files
        for filename, content in generated_files.items():
            file_path = agent_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return agent_dir


async def create_sample_agent():
    """Create a sample agent for testing."""
    
    # Sample requirements
    requirements = AgentRequirements(
        name="MVP Test Agent",
        description="A simple test agent for MVP validation",
        use_case="customer_service",
        channels=["web"],
        languages=["en"],
        stt_service=AIServiceConfig(name="deepgram", provider="deepgram"),
        llm_service=AIServiceConfig(name="openai", provider="openai"),
        tts_service=AIServiceConfig(name="cartesia", provider="cartesia"),
        knowledge_sources=[
            KnowledgeSourceConfig(type="web", source="https://docs.example.com")
        ],
        integrations=["twilio"]
    )
    
    # Build the agent
    builder = SimplePipecatAgentBuilder()
    await builder.initialize()
    
    result = await builder.build_agent(requirements)
    
    print("\n🎉 MVP Agent Built Successfully!")
    print("=" * 50)
    print(f"Agent Name: {result['agent_name']}")
    print(f"Directory: {result['agent_directory']}")
    print(f"Files: {', '.join(result['files_generated'])}")
    print(f"Knowledge Chunks: {result['knowledge_chunks']}")
    
    return result


async def interactive_builder():
    """Simple interactive builder for MVP testing."""
    
    print("\n🤖 Pipecat Agent Builder - MVP")
    print("=" * 40)
    print("Let's build a simple agent!")
    
    # Gather basic info
    name = input("\nAgent name: ") or "Test Agent"
    description = input("Description: ") or "A helpful AI agent"
    use_case = input("Use case (customer_service/assistant/other): ") or "assistant"
    
    # Create requirements
    requirements = AgentRequirements(
        name=name,
        description=description,
        use_case=use_case,
        channels=["web"],
        languages=["en"],
        stt_service=AIServiceConfig(name="deepgram", provider="deepgram"),
        llm_service=AIServiceConfig(name="openai", provider="openai"),
        tts_service=AIServiceConfig(name="cartesia", provider="cartesia")
    )
    
    # Build agent
    builder = SimplePipecatAgentBuilder()
    await builder.initialize()
    
    print(f"\n🏗️  Building {name}...")
    result = await builder.build_agent(requirements)
    
    print(f"\n✅ Success! Agent created at: {result['agent_directory']}")
    print("\nNext steps:")
    print(f"1. cd {result['agent_directory']}")
    print("2. Add your API keys to .env")
    print("3. pip install -r requirements.txt")
    print("4. python bot.py")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Pipecat Agent Builder MVP")
    parser.add_argument("--sample", action="store_true", help="Create a sample agent")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    if args.sample:
        asyncio.run(create_sample_agent())
    elif args.interactive:
        asyncio.run(interactive_builder())
    else:
        print("Usage: python mvp_main.py --sample | --interactive")
        print("\nMVP Mode - Simplified for testing:")
        print("- No complex validation")
        print("- Basic error handling")
        print("- Core functionality only")
        print("- Fast iteration")
