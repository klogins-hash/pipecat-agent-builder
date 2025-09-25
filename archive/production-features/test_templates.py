#!/usr/bin/env python3
"""Test template generation functionality."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import AgentRequirements, AIServiceConfig
from generation.templates import PipecatTemplateGenerator


class TestTemplateGeneration:
    """Test code template generation."""
    
    def test_generate_basic_agent_files(self):
        """Test basic agent file generation."""
        generator = PipecatTemplateGenerator()
        
        requirements = AgentRequirements(
            name="Test Agent",
            description="A test agent",
            use_case="customer_service",
            channels=["web"],
            languages=["en"],
            stt_service=AIServiceConfig(name="deepgram", provider="deepgram"),
            llm_service=AIServiceConfig(name="openai", provider="openai"),
            tts_service=AIServiceConfig(name="cartesia", provider="cartesia")
        )
        
        files = generator.generate_agent_files(requirements)
        
        # Check required files are generated
        required_files = ["bot.py", "Dockerfile", "requirements.txt", "pcc-deploy.toml"]
        for required_file in required_files:
            assert required_file in files
            assert len(files[required_file]) > 0
        
        # Check bot.py contains expected content
        bot_content = files["bot.py"]
        assert "Test Agent" in bot_content
        assert "DeepgramSTTService" in bot_content
        assert "OpenAILLMService" in bot_content
        assert "CartesiaTTSService" in bot_content
    
    def test_generate_phone_agent(self):
        """Test phone agent generation."""
        generator = PipecatTemplateGenerator()
        
        requirements = AgentRequirements(
            name="Phone Agent",
            description="Handles phone calls",
            use_case="customer_service",
            channels=["phone"],
            languages=["en"]
        )
        
        files = generator.generate_agent_files(requirements)
        bot_content = files["bot.py"]
        
        # Should use Daily transport for phone
        assert "DailyParams" in bot_content or "daily" in bot_content.lower()
    
    def test_generate_multilingual_agent(self):
        """Test multilingual agent generation."""
        generator = PipecatTemplateGenerator()
        
        requirements = AgentRequirements(
            name="Multilingual Agent",
            description="Supports multiple languages",
            use_case="customer_service",
            channels=["web"],
            languages=["en", "es", "fr"]
        )
        
        files = generator.generate_agent_files(requirements)
        bot_content = files["bot.py"]
        
        # Should contain multilingual support code
        assert len(requirements.languages) > 1
        assert "languages" in bot_content.lower() or "multilingual" in bot_content.lower()
    
    def test_generate_with_knowledge_sources(self):
        """Test agent with knowledge sources."""
        generator = PipecatTemplateGenerator()
        
        requirements = AgentRequirements(
            name="Knowledge Agent",
            description="Has knowledge sources",
            use_case="customer_service",
            channels=["web"],
            languages=["en"],
            knowledge_sources=[
                {"type": "web", "source": "https://example.com", "processing_options": {}}
            ]
        )
        
        files = generator.generate_agent_files(requirements)
        
        # Should generate knowledge processor
        assert "knowledge_processor.py" in files
        
        bot_content = files["bot.py"]
        knowledge_content = files["knowledge_processor.py"]
        
        # Bot should import and use knowledge processor
        assert "knowledge_processor" in bot_content.lower()
        assert "KnowledgeProcessor" in knowledge_content
    
    def test_dockerfile_generation(self):
        """Test Dockerfile generation."""
        generator = PipecatTemplateGenerator()
        
        requirements = AgentRequirements(
            name="Docker Test Agent",
            description="Test Dockerfile generation",
            use_case="customer_service",
            channels=["web"],
            languages=["en"]
        )
        
        files = generator.generate_agent_files(requirements)
        dockerfile = files["Dockerfile"]
        
        # Check Dockerfile contains expected elements
        assert "FROM python:" in dockerfile
        assert "COPY requirements.txt" in dockerfile
        assert "pip install" in dockerfile
        assert "CMD" in dockerfile
    
    def test_requirements_txt_generation(self):
        """Test requirements.txt generation."""
        generator = PipecatTemplateGenerator()
        
        requirements = AgentRequirements(
            name="Requirements Test Agent",
            description="Test requirements.txt generation",
            use_case="customer_service",
            channels=["web"],
            languages=["en"],
            stt_service=AIServiceConfig(name="deepgram", provider="deepgram"),
            llm_service=AIServiceConfig(name="openai", provider="openai"),
            tts_service=AIServiceConfig(name="cartesia", provider="cartesia")
        )
        
        files = generator.generate_agent_files(requirements)
        req_content = files["requirements.txt"]
        
        # Check requirements contains expected dependencies
        assert "pipecat-ai" in req_content
        assert "deepgram" in req_content.lower()
        assert "openai" in req_content.lower()
        assert "cartesia" in req_content.lower()
    
    def test_deployment_config_generation(self):
        """Test deployment configuration generation."""
        generator = PipecatTemplateGenerator()
        
        requirements = AgentRequirements(
            name="Deploy Test Agent",
            description="Test deployment config",
            use_case="customer_service",
            channels=["web"],
            languages=["en"]
        )
        
        files = generator.generate_agent_files(requirements)
        deploy_config = files["pcc-deploy.toml"]
        
        # Check deployment config contains expected elements
        assert "agent_name" in deploy_config
        assert "image" in deploy_config
        assert "secret_set" in deploy_config
        assert "[scaling]" in deploy_config


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
