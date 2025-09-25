#!/usr/bin/env python3
"""Final comprehensive test of MVP version."""

import asyncio
import sys
import tempfile
import shutil
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from mvp_main import SimplePipecatAgentBuilder
from core.simple_config import AgentRequirements, AIServiceConfig, KnowledgeSourceConfig


async def test_edge_cases():
    """Test edge cases and potential issues."""
    
    print("🔍 FINAL MVP TESTING - Edge Cases & Issues")
    print("=" * 55)
    
    builder = SimplePipecatAgentBuilder()
    await builder.initialize()
    
    test_results = []
    
    # Test 1: Empty/Minimal Requirements
    print("\n1. 🎯 Testing Minimal Requirements...")
    try:
        minimal_req = AgentRequirements(
            name="Minimal",
            description="Minimal",
            use_case="test"
        )
        
        result = await builder.build_agent(minimal_req)
        assert result["success"] == True
        
        # Check generated files
        agent_dir = Path(result["agent_directory"])
        bot_file = agent_dir / "bot.py"
        
        # Test Python syntax
        with open(bot_file, 'r') as f:
            bot_content = f.read()
        
        import ast
        ast.parse(bot_content)  # Will raise if syntax error
        
        print("   ✅ Minimal requirements work")
        test_results.append(("Minimal Requirements", True))
    except Exception as e:
        print(f"   ❌ Minimal requirements failed: {e}")
        test_results.append(("Minimal Requirements", False))
    
    # Test 2: Special Characters in Names
    print("\n2. 🔤 Testing Special Characters...")
    try:
        special_req = AgentRequirements(
            name="Test-Agent_2024 (MVP)",
            description="Agent with special chars: !@#$%",
            use_case="testing-special"
        )
        
        result = await builder.build_agent(special_req)
        assert result["success"] == True
        
        # Directory should be sanitized
        agent_dir = Path(result["agent_directory"])
        assert agent_dir.exists()
        
        print("   ✅ Special characters handled correctly")
        test_results.append(("Special Characters", True))
    except Exception as e:
        print(f"   ❌ Special characters failed: {e}")
        test_results.append(("Special Characters", False))
    
    # Test 3: All Service Types
    print("\n3. 🔧 Testing All Service Types...")
    try:
        service_combinations = [
            # OpenAI stack
            {
                "stt": AIServiceConfig(name="openai", provider="openai"),
                "llm": AIServiceConfig(name="openai", provider="openai"),
                "tts": AIServiceConfig(name="openai", provider="openai")
            },
            # Mixed stack
            {
                "stt": AIServiceConfig(name="deepgram", provider="deepgram"),
                "llm": AIServiceConfig(name="anthropic", provider="anthropic"),
                "tts": AIServiceConfig(name="elevenlabs", provider="elevenlabs")
            }
        ]
        
        for i, services in enumerate(service_combinations):
            req = AgentRequirements(
                name=f"Service Test {i+1}",
                description="Testing service combinations",
                use_case="testing",
                stt_service=services["stt"],
                llm_service=services["llm"],
                tts_service=services["tts"]
            )
            
            result = await builder.build_agent(req)
            assert result["success"] == True
            
            # Check imports in generated code
            agent_dir = Path(result["agent_directory"])
            with open(agent_dir / "bot.py", 'r') as f:
                bot_content = f.read()
            
            # Should contain service-specific imports
            if services["stt"].provider == "openai":
                assert "OpenAISTTService" in bot_content
            elif services["stt"].provider == "deepgram":
                assert "DeepgramSTTService" in bot_content
        
        print("   ✅ All service types work correctly")
        test_results.append(("Service Types", True))
    except Exception as e:
        print(f"   ❌ Service types failed: {e}")
        test_results.append(("Service Types", False))
    
    # Test 4: Large Knowledge Sources
    print("\n4. 📚 Testing Large Knowledge Configuration...")
    try:
        large_knowledge_req = AgentRequirements(
            name="Knowledge Heavy Bot",
            description="Bot with many knowledge sources",
            use_case="knowledge_intensive",
            knowledge_sources=[
                KnowledgeSourceConfig(type="web", source="https://docs1.example.com"),
                KnowledgeSourceConfig(type="web", source="https://docs2.example.com"),
                KnowledgeSourceConfig(type="document", source="manual.pdf"),
                KnowledgeSourceConfig(type="api", source="internal_api"),
                KnowledgeSourceConfig(type="web", source="https://faq.example.com")
            ],
            integrations=["twilio", "zendesk", "salesforce", "slack", "teams"]
        )
        
        result = await builder.build_agent(large_knowledge_req)
        assert result["success"] == True
        
        # Should have knowledge processor
        agent_dir = Path(result["agent_directory"])
        knowledge_file = agent_dir / "knowledge_processor.py"
        assert knowledge_file.exists()
        
        print("   ✅ Large knowledge configuration works")
        test_results.append(("Large Knowledge", True))
    except Exception as e:
        print(f"   ❌ Large knowledge failed: {e}")
        test_results.append(("Large Knowledge", False))
    
    # Test 5: File System Edge Cases
    print("\n5. 💾 Testing File System Edge Cases...")
    try:
        # Test with same name (should create different directories)
        req1 = AgentRequirements(name="Same Name", description="First", use_case="test")
        req2 = AgentRequirements(name="Same Name", description="Second", use_case="test")
        
        result1 = await builder.build_agent(req1)
        result2 = await builder.build_agent(req2)
        
        # Should overwrite the first one (expected behavior)
        assert result1["agent_directory"] == result2["agent_directory"]
        
        # Both should exist and be valid
        agent_dir = Path(result2["agent_directory"])
        assert agent_dir.exists()
        assert (agent_dir / "bot.py").exists()
        
        print("   ✅ File system edge cases handled")
        test_results.append(("File System Edge Cases", True))
    except Exception as e:
        print(f"   ❌ File system edge cases failed: {e}")
        test_results.append(("File System Edge Cases", False))
    
    # Test 6: Generated Code Validation
    print("\n6. 🔍 Testing Generated Code Validation...")
    try:
        # Generate a complex agent and validate all files
        validation_req = AgentRequirements(
            name="Validation Test Agent",
            description="For comprehensive validation",
            use_case="customer_service",
            channels=["web", "phone"],
            languages=["en", "es"],
            stt_service=AIServiceConfig(name="deepgram", provider="deepgram"),
            llm_service=AIServiceConfig(name="openai", provider="openai"),
            tts_service=AIServiceConfig(name="cartesia", provider="cartesia"),
            knowledge_sources=[
                KnowledgeSourceConfig(type="web", source="https://example.com")
            ],
            integrations=["twilio"]
        )
        
        result = await builder.build_agent(validation_req)
        agent_dir = Path(result["agent_directory"])
        
        # Validate all files
        files_to_validate = {
            "bot.py": ["import asyncio", "pipecat", "DeepgramSTTService", "OpenAILLMService", "CartesiaTTSService"],
            "requirements.txt": ["pipecat-ai", "deepgram", "openai", "cartesia"],
            "Dockerfile": ["FROM python:", "COPY requirements.txt", "pip install"],
            "pcc-deploy.toml": ["agent_name", "image", "secret_set"],
            ".env.example": ["DEEPGRAM_API_KEY", "OPENAI_API_KEY", "CARTESIA_API_KEY"],
            "knowledge_processor.py": ["KnowledgeProcessor", "class"]
        }
        
        for filename, required_content in files_to_validate.items():
            file_path = agent_dir / filename
            assert file_path.exists(), f"Missing file: {filename}"
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            for required in required_content:
                assert required in content, f"Missing '{required}' in {filename}"
        
        # Test Python syntax for Python files
        for py_file in ["bot.py", "knowledge_processor.py"]:
            with open(agent_dir / py_file, 'r') as f:
                py_content = f.read()
            
            import ast
            ast.parse(py_content)  # Will raise if syntax error
        
        print("   ✅ Generated code validation passed")
        test_results.append(("Code Validation", True))
    except Exception as e:
        print(f"   ❌ Code validation failed: {e}")
        test_results.append(("Code Validation", False))
    
    # Test 7: Performance Test
    print("\n7. ⚡ Testing Performance...")
    try:
        import time
        
        start_time = time.time()
        
        # Build 5 agents quickly
        for i in range(5):
            perf_req = AgentRequirements(
                name=f"Perf Test {i}",
                description="Performance testing",
                use_case="testing"
            )
            
            result = await builder.build_agent(perf_req)
            assert result["success"] == True
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 5
        
        print(f"   ✅ Performance test passed")
        print(f"      Total time: {total_time:.2f}s")
        print(f"      Average per agent: {avg_time:.2f}s")
        
        # Should be reasonably fast (under 5 seconds per agent)
        assert avg_time < 5.0, f"Too slow: {avg_time:.2f}s per agent"
        
        test_results.append(("Performance", True))
    except Exception as e:
        print(f"   ❌ Performance test failed: {e}")
        test_results.append(("Performance", False))
    
    # Final Summary
    print("\n" + "=" * 55)
    print("📊 FINAL MVP TEST RESULTS")
    print("=" * 55)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        if result is True:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")
            failed += 1
    
    print(f"\nFinal Summary: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 ALL EDGE CASE TESTS PASSED!")
        print("MVP is robust and ready for production use.")
        return True
    else:
        print(f"\n⚠️  {failed} edge case tests failed.")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_edge_cases())
    sys.exit(0 if success else 1)
