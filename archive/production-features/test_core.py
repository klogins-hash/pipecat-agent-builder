#!/usr/bin/env python3
"""Core component tests for Pipecat Agent Builder."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import AgentRequirements, AIServiceConfig, DeploymentConfig, KnowledgeSourceConfig
from core.exceptions import *
from core.validators import SecurityValidator, RequirementsValidator, ResourceValidator
from core.monitoring import MetricsCollector


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
            "http://localhost:8080",
            "https://192.168.1.1",
            "not-a-url",
            ""
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValidationError):
                SecurityValidator.validate_url(url)


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


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
