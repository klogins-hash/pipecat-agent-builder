#!/usr/bin/env python3
"""Comprehensive test suite for Pipecat Agent Builder."""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import AgentRequirements, AIServiceConfig, DeploymentConfig, KnowledgeSourceConfig
from core.exceptions import *
from core.validators import SecurityValidator, RequirementsValidator, APIKeyValidator, ResourceValidator
from core.monitoring import MetricsCollector, BuildSession
from knowledge.vectorizer import PipecatDocumentationVectorizer
from generation.templates import PipecatTemplateGenerator
from main import PipecatAgentBuilder


class TestSecurityValidator:
    """Test security validation functionality."""
    
    def test_validate_agent_name_valid(self):
        """Test valid agent names."""
        valid_names = [
            "Customer Service Bot",
            "Personal-Assistant",
            "AI_Helper_2024",
            "Simple Bot"
        ]
        
        for name in valid_names:
            result = SecurityValidator.validate_agent_name(name)
            assert result == name.strip()
    
    def test_validate_agent_name_invalid(self):
        """Test invalid agent names."""
        invalid_names = [
            "",
            "   ",
            "Bot with __import__ code",
            "eval('malicious')",
            "x" * 101,  # Too long
            "Bot<script>alert(1)</script>",
        ]
        
        for name in invalid_names:
            with pytest.raises(ValidationError):
                SecurityValidator.validate_agent_name(name)
    
    def test_validate_url_valid(self):
        """Test valid URLs."""
        valid_urls = [
            "https://docs.example.com",
            "http://api.service.com/v1",
            "https://knowledge.company.org/faq"
        ]
        
        for url in valid_urls:
            result = SecurityValidator.validate_url(url)
            assert result == url
    
    def test_validate_url_invalid(self):
        """Test invalid URLs."""
        invalid_urls = [
            "ftp://file.server.com",
            "javascript:alert(1)",
            "http://localhost:8080",
            "https://192.168.1.1",
            "not-a-url",
            ""
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValidationError):
                SecurityValidator.validate_url(url)
    
    def test_validate_file_path_valid(self):
        """Test valid file paths."""
        valid_paths = [
            "documents/faq.pdf",
            "knowledge/manual.txt",
            "data.json"
        ]
        
        for path in valid_paths:
            result = SecurityValidator.validate_file_path(path)
            assert result == path
    
    def test_validate_file_path_invalid(self):
        """Test invalid file paths."""
        invalid_paths = [
            "../../../etc/passwd",
            "/etc/shadow",
            "../../config.ini",
            "/usr/bin/malicious"
        ]
        
        for path in invalid_paths:
            with pytest.raises(ValidationError):
                SecurityValidator.validate_file_path(path)


class TestRequirementsValidator:
    """Test requirements validation."""
    
    def test_validate_requirements_valid(self):
        """Test valid requirements."""
        requirements = AgentRequirements(
            name="Test Agent",
            description="A test agent for validation",
            use_case="customer_service",
            channels=["web", "phone"],
            languages=["en", "es"],
            knowledge_sources=[
                KnowledgeSourceConfig(
                    type="web",
                    source="https://docs.example.com"
                )
            ],
            integrations=["twilio", "zendesk"]
        )
        
        validated = RequirementsValidator.validate_requirements(requirements)
        assert validated.name == "Test Agent"
        assert "web" in validated.channels
        assert "en" in validated.languages
    
    def test_validate_requirements_invalid_channels(self):
        """Test invalid channels."""
        requirements = AgentRequirements(
            name="Test Agent",
            description="A test agent",
            use_case="customer_service",
            channels=["invalid_channel"],
            languages=["en"]
        )
        
        with pytest.raises(ValidationError):
            RequirementsValidator.validate_requirements(requirements)
    
    def test_validate_requirements_invalid_languages(self):
        """Test invalid languages."""
        requirements = AgentRequirements(
            name="Test Agent",
            description="A test agent",
            use_case="customer_service",
            channels=["web"],
            languages=["invalid_lang"]
        )
        
        with pytest.raises(ValidationError):
            RequirementsValidator.validate_requirements(requirements)


class TestResourceValidator:
    """Test resource validation and estimation."""
    
    def test_validate_resource_limits_valid(self):
        """Test valid resource limits."""
        requirements = AgentRequirements(
            name="Test Agent",
            description="A test agent",
            use_case="customer_service",
            channels=["web"],
            languages=["en"],
            knowledge_sources=[
                KnowledgeSourceConfig(type="web", source="https://example.com")
            ],
            integrations=["twilio"]
        )
        
        # Should not raise exception
        ResourceValidator.validate_resource_limits(requirements)
    
    def test_validate_resource_limits_too_many_sources(self):
        """Test too many knowledge sources."""
        knowledge_sources = [
            KnowledgeSourceConfig(type="web", source=f"https://example{i}.com")
            for i in range(15)  # Exceeds limit
        ]
        
        requirements = AgentRequirements(
            name="Test Agent",
            description="A test agent",
            use_case="customer_service",
            channels=["web"],
            languages=["en"],
            knowledge_sources=knowledge_sources
        )
        
        with pytest.raises(ValidationError):
            ResourceValidator.validate_resource_limits(requirements)
    
    def test_estimate_resource_usage(self):
        """Test resource usage estimation."""
        requirements = AgentRequirements(
            name="Test Agent",
            description="A test agent",
            use_case="customer_service",
            channels=["web", "phone"],
            languages=["en", "es"],
            knowledge_sources=[
                KnowledgeSourceConfig(type="web", source="https://example.com")
            ],
            integrations=["twilio"]
        )
        
        estimate = ResourceValidator.estimate_resource_usage(requirements)
        
        assert "estimated_cpu_units" in estimate
        assert "estimated_memory_mb" in estimate
        assert "estimated_storage_mb" in estimate
        assert "complexity_score" in estimate
        
        assert estimate["estimated_cpu_units"] > 1.0  # Should be higher due to multiple features
        assert estimate["complexity_score"] in ["simple", "moderate", "complex"]


class TestMetricsCollector:
    """Test metrics collection functionality."""
    
    def test_record_metric(self):
        """Test metric recording."""
        collector = MetricsCollector()
        
        collector.record_metric("test_metric", 42.0, {"label": "test"})
        
        assert "test_metric" in collector.metrics
        assert len(collector.metrics["test_metric"]) == 1
        
        point = collector.metrics["test_metric"][0]
        assert point.value == 42.0
        assert point.labels["label"] == "test"
    
    def test_increment_counter(self):
        """Test counter increment."""
        collector = MetricsCollector()
        
        collector.increment_counter("test_counter")
        collector.increment_counter("test_counter")
        
        # Should have recorded two metric points
        assert len(collector.metrics["test_counter"]) == 2
        
        # Values should be 1 and 2
        values = [p.value for p in collector.metrics["test_counter"]]
        assert values == [1, 2]
    
    def test_session_tracking(self):
        """Test build session tracking."""
        collector = MetricsCollector()
        
        session = collector.start_session("test-session", "Test Agent", "customer_service")
        
        assert session.session_id == "test-session"
        assert session.agent_name == "Test Agent"
        assert session.use_case == "customer_service"
        assert session.status == "in_progress"
        
        collector.end_session("test-session", "completed")
        
        assert session.status == "completed"
        assert session.end_time is not None
    
    def test_session_stats(self):
        """Test session statistics."""
        collector = MetricsCollector()
        
        # Create some test sessions
        collector.start_session("session1", "Agent1", "customer_service")
        collector.end_session("session1", "completed")
        
        collector.start_session("session2", "Agent2", "education")
        collector.end_session("session2", "failed", "Test error")
        
        stats = collector.get_session_stats()
        
        assert stats["total_sessions"] == 2
        assert stats["completed_sessions"] == 1
        assert stats["failed_sessions"] == 1
        assert stats["success_rate"] == 0.5


class TestTemplateGenerator:
    """Test code template generation."""
    
    def test_generate_agent_files(self):
        """Test agent file generation."""
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
        assert "multilingual" in bot_content.lower() or "languages" in bot_content.lower()


@pytest.mark.asyncio
class TestPipecatAgentBuilder:
    """Test main application functionality."""
    
    async def test_initialization_success(self):
        """Test successful initialization."""
        with patch('main.PipecatDocumentationVectorizer') as mock_vectorizer:
            mock_instance = Mock()
            mock_instance.get_stats.return_value = {"total_chunks": 100}
            mock_vectorizer.return_value = mock_instance
            
            builder = PipecatAgentBuilder()
            
            # Mock API key validation
            with patch('core.validators.APIKeyValidator.validate_api_keys') as mock_validate:
                mock_validate.return_value = {
                    'openai_api_key': True,
                    'deepgram_api_key': True,
                    'cartesia_api_key': True
                }
                
                await builder.initialize()
                
                assert builder.vectorizer is not None
    
    async def test_initialization_missing_api_keys(self):
        """Test initialization with missing API keys."""
        builder = PipecatAgentBuilder()
        
        with patch('core.validators.APIKeyValidator.validate_api_keys') as mock_validate:
            mock_validate.return_value = {
                'openai_api_key': False,
                'deepgram_api_key': True,
                'cartesia_api_key': True
            }
            
            with pytest.raises(APIKeyError):
                await builder.initialize()
    
    async def test_code_generation_fallback(self):
        """Test code generation with Cascade fallback to templates."""
        builder = PipecatAgentBuilder()
        builder.template_generator = Mock()
        builder.template_generator.generate_agent_files.return_value = {
            "bot.py": "# Generated bot code",
            "requirements.txt": "pipecat-ai[all]"
        }
        
        requirements = AgentRequirements(
            name="Test Agent",
            description="Test description",
            use_case="customer_service",
            channels=["web"],
            languages=["en"]
        )
        
        # Mock Cascade failure
        with patch('mcp.cascade_client.CascadeOrchestrator') as mock_cascade:
            mock_cascade.side_effect = MCPConnectionError("Connection failed")
            
            files = await builder._generate_agent_code_with_fallback(requirements, [])
            
            assert "bot.py" in files
            assert "requirements.txt" in files
            builder.template_generator.generate_agent_files.assert_called_once()
    
    async def test_code_validation(self):
        """Test generated code validation."""
        builder = PipecatAgentBuilder()
        
        # Valid code
        valid_files = {
            "bot.py": "import asyncio\nimport pipecat\nprint('hello')",
            "requirements.txt": "pipecat-ai[all]>=0.0.50",
            "Dockerfile": "FROM python:3.11"
        }
        
        result = await builder._validate_generated_code(valid_files)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        
        # Invalid code (syntax error)
        invalid_files = {
            "bot.py": "import asyncio\nprint('hello'  # Missing closing parenthesis",
            "requirements.txt": "pipecat-ai[all]>=0.0.50",
            "Dockerfile": "FROM python:3.11"
        }
        
        result = await builder._validate_generated_code(invalid_files)
        assert result["valid"] is False
        assert len(result["errors"]) > 0


class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_template_generation(self):
        """Test complete agent generation using templates."""
        # Create temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock settings
            with patch('core.config.settings') as mock_settings:
                mock_settings.output_path = temp_dir
                mock_settings.chroma_persist_directory = temp_dir + "/chroma"
                mock_settings.docs_path = temp_dir + "/docs"
                
                # Create mock docs directory
                docs_dir = Path(temp_dir) / "docs"
                docs_dir.mkdir()
                (docs_dir / "test.md").write_text("# Test Documentation")
                
                builder = PipecatAgentBuilder()
                builder.template_generator = PipecatTemplateGenerator()
                
                requirements = AgentRequirements(
                    name="Integration Test Agent",
                    description="An agent for integration testing",
                    use_case="customer_service",
                    channels=["web"],
                    languages=["en"]
                )
                
                # Generate files
                files = await builder._generate_agent_code_with_fallback(requirements, [])
                
                # Save files
                agent_dir = await builder._save_generated_files(requirements, files)
                
                # Verify files were created
                assert agent_dir.exists()
                assert (agent_dir / "bot.py").exists()
                assert (agent_dir / "requirements.txt").exists()
                assert (agent_dir / "Dockerfile").exists()
                
                # Verify content
                bot_content = (agent_dir / "bot.py").read_text()
                assert "Integration Test Agent" in bot_content


# Test fixtures and utilities
@pytest.fixture
def sample_requirements():
    """Sample requirements for testing."""
    return AgentRequirements(
        name="Sample Agent",
        description="A sample agent for testing",
        use_case="customer_service",
        channels=["web", "phone"],
        languages=["en", "es"],
        stt_service=AIServiceConfig(name="deepgram", provider="deepgram"),
        llm_service=AIServiceConfig(name="openai", provider="openai"),
        tts_service=AIServiceConfig(name="cartesia", provider="cartesia"),
        knowledge_sources=[
            KnowledgeSourceConfig(type="web", source="https://docs.example.com")
        ],
        integrations=["twilio", "zendesk"],
        deployment=DeploymentConfig(scaling_min=1, scaling_max=5)
    )


@pytest.fixture
def metrics_collector():
    """Fresh metrics collector for testing."""
    return MetricsCollector()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
