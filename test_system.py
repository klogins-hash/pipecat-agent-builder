#!/usr/bin/env python3
"""Quick system test for Pipecat Agent Builder."""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import settings, AgentRequirements, AIServiceConfig, DeploymentConfig
from core.logger import setup_logger
from knowledge.vectorizer import PipecatDocumentationVectorizer
from generation.templates import PipecatTemplateGenerator

logger = setup_logger("test_system")


async def test_configuration():
    """Test configuration loading."""
    logger.info("Testing configuration...")
    
    try:
        # Test settings
        assert settings.docs_path is not None
        assert settings.chroma_persist_directory is not None
        logger.info("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False


async def test_vectorizer():
    """Test documentation vectorizer."""
    logger.info("Testing vectorizer...")
    
    try:
        vectorizer = PipecatDocumentationVectorizer()
        
        # Test if we can initialize
        stats = vectorizer.get_stats()
        logger.info(f"Vector database stats: {stats}")
        
        # Test search if we have data
        if stats["total_chunks"] > 0:
            results = await vectorizer.search("voice assistant", n_results=2)
            logger.info(f"Search test returned {len(results)} results")
        
        logger.info("✅ Vectorizer test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Vectorizer test failed: {e}")
        return False


async def test_template_generation():
    """Test template generation."""
    logger.info("Testing template generation...")
    
    try:
        generator = PipecatTemplateGenerator()
        
        # Create test requirements
        requirements = AgentRequirements(
            name="Test Agent",
            description="A test agent for validation",
            use_case="testing",
            channels=["web"],
            languages=["en"],
            stt_service=AIServiceConfig(name="deepgram", provider="deepgram"),
            llm_service=AIServiceConfig(name="openai", provider="openai"),
            tts_service=AIServiceConfig(name="cartesia", provider="cartesia"),
        )
        
        # Generate files
        files = generator.generate_agent_files(requirements)
        
        # Check that we got expected files
        expected_files = ["bot.py", "Dockerfile", "requirements.txt", "pcc-deploy.toml"]
        for expected_file in expected_files:
            if expected_file not in files:
                raise Exception(f"Missing expected file: {expected_file}")
        
        # Check that files have content
        for filename, content in files.items():
            if not content.strip():
                raise Exception(f"Empty file generated: {filename}")
        
        logger.info(f"✅ Template generation test passed - generated {len(files)} files")
        return True
    except Exception as e:
        logger.error(f"❌ Template generation test failed: {e}")
        return False


async def test_requirements_model():
    """Test requirements data model."""
    logger.info("Testing requirements model...")
    
    try:
        # Test creating requirements
        requirements = AgentRequirements(
            name="Test Agent",
            description="Test description",
            use_case="customer_service",
            channels=["phone", "web"],
            languages=["en", "es"]
        )
        
        # Test serialization
        req_dict = requirements.model_dump()
        assert req_dict["name"] == "Test Agent"
        assert "phone" in req_dict["channels"]
        
        logger.info("✅ Requirements model test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Requirements model test failed: {e}")
        return False


async def run_system_test():
    """Run all system tests."""
    logger.info("Starting Pipecat Agent Builder system test...")
    
    tests = [
        ("Configuration", test_configuration),
        ("Requirements Model", test_requirements_model),
        ("Template Generation", test_template_generation),
        ("Vectorizer", test_vectorizer),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running test: {test_name}")
        try:
            success = await test_func()
            if success:
                passed += 1
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
    
    logger.info(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! System is ready.")
        return True
    else:
        logger.warning("⚠️  Some tests failed. Check the logs above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_system_test())
    sys.exit(0 if success else 1)
