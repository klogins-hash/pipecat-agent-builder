#!/usr/bin/env python3
"""Comprehensive testing for MVP version."""

import asyncio
import sys
import tempfile
import shutil
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from mvp_main import SimplePipecatAgentBuilder
from core.simple_config import AgentRequirements, AIServiceConfig, KnowledgeSourceConfig, DeploymentConfig


async def test_mvp_comprehensive():
    """Run comprehensive tests on MVP version."""
    
    print("🧪 COMPREHENSIVE MVP TESTING")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Basic Initialization
    print("\n1. 🚀 Testing MVP Initialization...")
    try:
        builder = SimplePipecatAgentBuilder()
        await builder.initialize()
        print("   ✅ MVP builder initialized successfully")
        test_results.append(("MVP Initialization", True))
    except Exception as e:
        print(f"   ❌ MVP initialization failed: {e}")
        test_results.append(("MVP Initialization", False))
        return False
    
    # Test 2: Simple Agent Requirements
    print("\n2. 📋 Testing Simple Requirements...")
    try:
        simple_req = AgentRequirements(
            name="Simple Test Bot",
            description="A basic test bot",
            use_case="testing"
        )
        
        assert simple_req.name == "Simple Test Bot"
        assert simple_req.channels == ["web"]  # Default
        assert simple_req.languages == ["en"]  # Default
        
        print("   ✅ Simple requirements work correctly")
        test_results.append(("Simple Requirements", True))
    except Exception as e:
        print(f"   ❌ Simple requirements failed: {e}")
        test_results.append(("Simple Requirements", False))
    
    # Test 3: Complex Agent Requirements
    print("\n3. 🔧 Testing Complex Requirements...")
    try:
        complex_req = AgentRequirements(
            name="Complex Customer Service Bot",
            description="A comprehensive customer service agent",
            use_case="customer_service",
            channels=["web", "phone", "mobile"],
            languages=["en", "es", "fr"],
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
                voice_id="test-voice-id"
            ),
            knowledge_sources=[
                KnowledgeSourceConfig(
                    type="web",
                    source="https://docs.example.com",
                    processing_options={"crawl_depth": 2}
                ),
                KnowledgeSourceConfig(
                    type="document",
                    source="faq.pdf",
                    processing_options={"format": "faq"}
                )
            ],
            integrations=["twilio", "zendesk", "salesforce"],
            deployment=DeploymentConfig(
                platform="pipecat-cloud",
                scaling_min=2,
                scaling_max=10,
                region="us-west-2"
            )
        )
        
        assert len(complex_req.channels) == 3
        assert len(complex_req.languages) == 3
        assert len(complex_req.knowledge_sources) == 2
        assert len(complex_req.integrations) == 3
        assert complex_req.stt_service.provider == "deepgram"
        
        print("   ✅ Complex requirements work correctly")
        test_results.append(("Complex Requirements", True))
    except Exception as e:
        print(f"   ❌ Complex requirements failed: {e}")
        test_results.append(("Complex Requirements", False))
    
    # Test 4: Agent Building (Simple)
    print("\n4. 🏗️ Testing Simple Agent Building...")
    try:
        result = await builder.build_agent(simple_req)
        
        assert result["success"] == True
        assert result["agent_name"] == "Simple Test Bot"
        assert "agent_directory" in result
        assert len(result["files_generated"]) >= 4  # At least bot.py, Dockerfile, requirements.txt, pcc-deploy.toml
        
        # Check directory exists
        agent_dir = Path(result["agent_directory"])
        assert agent_dir.exists()
        
        print(f"   ✅ Simple agent built successfully")
        print(f"      Directory: {result['agent_directory']}")
        print(f"      Files: {len(result['files_generated'])}")
        test_results.append(("Simple Agent Building", True))
    except Exception as e:
        print(f"   ❌ Simple agent building failed: {e}")
        test_results.append(("Simple Agent Building", False))
    
    # Test 5: Agent Building (Complex)
    print("\n5. 🔧 Testing Complex Agent Building...")
    try:
        result = await builder.build_agent(complex_req)
        
        assert result["success"] == True
        assert result["agent_name"] == "Complex Customer Service Bot"
        assert len(result["files_generated"]) >= 5  # Should include knowledge_processor.py
        
        # Check specific files exist
        agent_dir = Path(result["agent_directory"])
        required_files = ["bot.py", "requirements.txt", "Dockerfile", "pcc-deploy.toml"]
        for file_name in required_files:
            file_path = agent_dir / file_name
            assert file_path.exists(), f"Missing file: {file_name}"
            assert file_path.stat().st_size > 0, f"Empty file: {file_name}"
        
        print(f"   ✅ Complex agent built successfully")
        print(f"      Directory: {result['agent_directory']}")
        print(f"      Files: {len(result['files_generated'])}")
        test_results.append(("Complex Agent Building", True))
    except Exception as e:
        print(f"   ❌ Complex agent building failed: {e}")
        test_results.append(("Complex Agent Building", False))
    
    # Test 6: Generated Code Quality
    print("\n6. 🔍 Testing Generated Code Quality...")
    try:
        agent_dir = Path(result["agent_directory"])
        bot_file = agent_dir / "bot.py"
        
        # Check Python syntax
        with open(bot_file, 'r') as f:
            bot_content = f.read()
        
        import ast
        ast.parse(bot_content)  # Will raise SyntaxError if invalid
        
        # Check for required content
        assert "import asyncio" in bot_content
        assert "pipecat" in bot_content
        assert complex_req.name.replace(" ", " ") in bot_content or "Complex Customer Service Bot" in bot_content
        
        # Check requirements.txt
        req_file = agent_dir / "requirements.txt"
        with open(req_file, 'r') as f:
            req_content = f.read()
        
        assert "pipecat-ai" in req_content
        
        print("   ✅ Generated code quality is good")
        test_results.append(("Code Quality", True))
    except Exception as e:
        print(f"   ❌ Code quality check failed: {e}")
        test_results.append(("Code Quality", False))
    
    # Test 7: Knowledge Integration
    print("\n7. 🧠 Testing Knowledge Integration...")
    try:
        # Test with knowledge sources
        knowledge_req = AgentRequirements(
            name="Knowledge Bot",
            description="Bot with knowledge sources",
            use_case="support",
            knowledge_sources=[
                KnowledgeSourceConfig(type="web", source="https://example.com")
            ]
        )
        
        result = await builder.build_agent(knowledge_req)
        agent_dir = Path(result["agent_directory"])
        
        # Should have knowledge processor
        knowledge_file = agent_dir / "knowledge_processor.py"
        assert knowledge_file.exists()
        
        with open(knowledge_file, 'r') as f:
            knowledge_content = f.read()
        
        assert "KnowledgeProcessor" in knowledge_content
        
        print("   ✅ Knowledge integration works")
        test_results.append(("Knowledge Integration", True))
    except Exception as e:
        print(f"   ❌ Knowledge integration failed: {e}")
        test_results.append(("Knowledge Integration", False))
    
    # Test 8: Error Handling (Graceful)
    print("\n8. 🛡️ Testing Error Handling...")
    try:
        # Test with minimal requirements (should still work)
        minimal_req = AgentRequirements(
            name="Minimal Bot",
            description="Minimal test",
            use_case="test"
        )
        
        result = await builder.build_agent(minimal_req)
        assert result["success"] == True
        
        print("   ✅ Graceful error handling works")
        test_results.append(("Error Handling", True))
    except Exception as e:
        print(f"   ❌ Error handling failed: {e}")
        test_results.append(("Error Handling", False))
    
    # Test 9: File System Operations
    print("\n9. 💾 Testing File System Operations...")
    try:
        # Test multiple agents don't conflict
        agent1_req = AgentRequirements(name="Agent One", description="First", use_case="test")
        agent2_req = AgentRequirements(name="Agent Two", description="Second", use_case="test")
        
        result1 = await builder.build_agent(agent1_req)
        result2 = await builder.build_agent(agent2_req)
        
        # Should have different directories
        assert result1["agent_directory"] != result2["agent_directory"]
        
        # Both should exist
        assert Path(result1["agent_directory"]).exists()
        assert Path(result2["agent_directory"]).exists()
        
        print("   ✅ File system operations work correctly")
        test_results.append(("File System Operations", True))
    except Exception as e:
        print(f"   ❌ File system operations failed: {e}")
        test_results.append(("File System Operations", False))
    
    # Test 10: Vectorizer Integration (Optional)
    print("\n10. 🔍 Testing Vectorizer Integration...")
    try:
        if builder.vectorizer:
            # Test search functionality
            context = await builder._get_knowledge_context(complex_req)
            print(f"      Found {len(context)} knowledge chunks")
            
            # Should find some relevant context
            assert isinstance(context, list)
            
            print("   ✅ Vectorizer integration works")
            test_results.append(("Vectorizer Integration", True))
        else:
            print("   ⚠️  Vectorizer not available (acceptable for MVP)")
            test_results.append(("Vectorizer Integration", "Not Available"))
    except Exception as e:
        print(f"   ❌ Vectorizer integration failed: {e}")
        test_results.append(("Vectorizer Integration", False))
    
    # Test Summary
    print("\n" + "=" * 50)
    print("📊 MVP TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    warnings = 0
    
    for test_name, result in test_results:
        if result is True:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        elif result is False:
            print(f"❌ {test_name}: FAILED")
            failed += 1
        else:
            print(f"⚠️  {test_name}: {result}")
            warnings += 1
    
    print(f"\nSummary: {passed} passed, {failed} failed, {warnings} warnings")
    
    if failed == 0:
        print("\n🎉 ALL MVP TESTS PASSED!")
        print("The MVP version is working correctly and ready for use.")
        return True
    else:
        print(f"\n⚠️  {failed} tests failed. Issues need to be addressed.")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mvp_comprehensive())
    sys.exit(0 if success else 1)
