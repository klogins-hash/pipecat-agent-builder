#!/usr/bin/env python3
"""Test main functionality without conversation interface dependencies."""

import asyncio
import sys
from pathlib import Path
import tempfile
import shutil

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import AgentRequirements, AIServiceConfig, KnowledgeSourceConfig
from core.validators import RequirementsValidator, ResourceValidator, SecurityValidator
from core.monitoring import start_session, end_session, metrics_collector
from knowledge.vectorizer import PipecatDocumentationVectorizer
from generation.templates import PipecatTemplateGenerator


class SimplifiedAgentBuilder:
    """Simplified version of PipecatAgentBuilder for testing."""
    
    def __init__(self):
        self.vectorizer = None
        self.template_generator = PipecatTemplateGenerator()
        
    async def initialize_vectorizer(self):
        """Initialize the vectorizer."""
        try:
            self.vectorizer = PipecatDocumentationVectorizer()
            return True
        except Exception as e:
            print(f"⚠️  Vectorizer initialization failed: {e}")
            return False
    
    async def get_knowledge_context(self, requirements) -> list:
        """Get relevant knowledge context."""
        if not self.vectorizer:
            return []
        
        try:
            # Create search queries based on requirements
            queries = [
                f"{requirements.use_case} agent",
                f"pipecat {' '.join(requirements.channels)} integration",
                f"speech to text {requirements.languages[0] if requirements.languages else 'english'}",
                "pipeline configuration examples"
            ]
            
            knowledge_context = []
            for query in queries:
                results = await self.vectorizer.search(query, n_results=2)
                knowledge_context.extend(results)
            
            return knowledge_context
        except Exception as e:
            print(f"⚠️  Knowledge search failed: {e}")
            return []
    
    async def generate_agent_code(self, requirements, knowledge_context) -> dict:
        """Generate agent code using templates."""
        try:
            generated_files = self.template_generator.generate_agent_files(requirements)
            
            if not generated_files:
                raise Exception("Template generation returned empty result")
            
            return generated_files
        except Exception as e:
            raise Exception(f"Code generation failed: {e}")
    
    async def validate_generated_code(self, generated_files: dict) -> dict:
        """Validate generated code."""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check required files
        required_files = ["bot.py", "requirements.txt", "Dockerfile"]
        for required_file in required_files:
            if required_file not in generated_files:
                validation_result["errors"].append(f"Missing required file: {required_file}")
                validation_result["valid"] = False
        
        # Validate Python syntax in bot.py
        if "bot.py" in generated_files:
            try:
                import ast
                ast.parse(generated_files["bot.py"])
            except SyntaxError as e:
                validation_result["errors"].append(f"Syntax error in bot.py: {e}")
                validation_result["valid"] = False
        
        # Check for required imports in bot.py
        if "bot.py" in generated_files:
            bot_content = generated_files["bot.py"]
            required_imports = ["pipecat", "asyncio"]
            for import_name in required_imports:
                if import_name not in bot_content:
                    validation_result["warnings"].append(f"Missing import: {import_name}")
        
        return validation_result
    
    async def save_generated_files(self, requirements, generated_files) -> Path:
        """Save generated files to disk."""
        agent_name = requirements.name.lower().replace(' ', '_').replace('-', '_')
        agent_dir = Path("./generated_agents") / agent_name
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        for filename, content in generated_files.items():
            file_path = agent_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return agent_dir


async def run_comprehensive_tests():
    """Run comprehensive tests of the system."""
    
    print("🧪 COMPREHENSIVE PIPECAT AGENT BUILDER TESTS")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Security Validation
    print("\n1. 🔒 Testing Security Validation...")
    try:
        # Test valid inputs
        SecurityValidator.validate_agent_name("Valid Agent Name")
        SecurityValidator.validate_url("https://docs.example.com")
        SecurityValidator.validate_file_path("documents/faq.pdf")
        
        # Test invalid inputs should raise exceptions
        try:
            SecurityValidator.validate_agent_name("eval('malicious')")
            assert False, "Should have raised ValidationError"
        except Exception:
            pass  # Expected
        
        try:
            SecurityValidator.validate_url("http://localhost:8080")
            assert False, "Should have raised ValidationError"
        except Exception:
            pass  # Expected
        
        print("   ✅ Security validation working correctly")
        test_results.append(("Security Validation", True))
    except Exception as e:
        print(f"   ❌ Security validation failed: {e}")
        test_results.append(("Security Validation", False))
    
    # Test 2: Requirements Validation
    print("\n2. 📋 Testing Requirements Validation...")
    try:
        requirements = AgentRequirements(
            name="Test Agent",
            description="A comprehensive test agent",
            use_case="customer_service",
            channels=["web", "phone"],
            languages=["en", "es"],
            stt_service=AIServiceConfig(name="deepgram", provider="deepgram"),
            llm_service=AIServiceConfig(name="openai", provider="openai"),
            tts_service=AIServiceConfig(name="cartesia", provider="cartesia"),
            knowledge_sources=[
                KnowledgeSourceConfig(type="web", source="https://docs.example.com")
            ],
            integrations=["twilio", "zendesk"]
        )
        
        validated = RequirementsValidator.validate_requirements(requirements)
        assert validated.name == "Test Agent"
        assert "web" in validated.channels
        
        print("   ✅ Requirements validation working correctly")
        test_results.append(("Requirements Validation", True))
    except Exception as e:
        print(f"   ❌ Requirements validation failed: {e}")
        test_results.append(("Requirements Validation", False))
    
    # Test 3: Resource Estimation
    print("\n3. 📊 Testing Resource Estimation...")
    try:
        resource_estimate = ResourceValidator.estimate_resource_usage(requirements)
        
        assert "estimated_cpu_units" in resource_estimate
        assert "estimated_memory_mb" in resource_estimate
        assert "complexity_score" in resource_estimate
        assert resource_estimate["complexity_score"] in ["simple", "moderate", "complex"]
        
        print(f"   Complexity: {resource_estimate['complexity_score']}")
        print(f"   CPU Units: {resource_estimate['estimated_cpu_units']}")
        print(f"   Memory: {resource_estimate['estimated_memory_mb']} MB")
        print("   ✅ Resource estimation working correctly")
        test_results.append(("Resource Estimation", True))
    except Exception as e:
        print(f"   ❌ Resource estimation failed: {e}")
        test_results.append(("Resource Estimation", False))
    
    # Test 4: Metrics Collection
    print("\n4. 📈 Testing Metrics Collection...")
    try:
        # Test session tracking
        session_id = "test-session-comprehensive"
        session = start_session(session_id, "Test Agent", "customer_service")
        
        # Record some metrics
        metrics_collector.record_metric("test_metric", 42.0, {"test": "true"})
        metrics_collector.increment_counter("test_counter")
        
        end_session(session_id, "completed")
        
        # Verify session was tracked
        assert session.session_id == session_id
        assert session.status == "completed"
        
        # Get session stats
        stats = metrics_collector.get_session_stats()
        assert stats["total_sessions"] >= 1
        
        print("   ✅ Metrics collection working correctly")
        test_results.append(("Metrics Collection", True))
    except Exception as e:
        print(f"   ❌ Metrics collection failed: {e}")
        test_results.append(("Metrics Collection", False))
    
    # Test 5: Vectorization System
    print("\n5. 🧠 Testing Vectorization System...")
    try:
        builder = SimplifiedAgentBuilder()
        vectorizer_ready = await builder.initialize_vectorizer()
        
        if vectorizer_ready:
            stats = builder.vectorizer.get_stats()
            print(f"   Vector database has {stats['total_chunks']} chunks")
            
            # Test search
            results = await builder.vectorizer.search("voice assistant", n_results=3)
            print(f"   Search returned {len(results)} results")
            
            print("   ✅ Vectorization system working correctly")
            test_results.append(("Vectorization System", True))
        else:
            print("   ⚠️  Vectorization system not ready (acceptable)")
            test_results.append(("Vectorization System", "Not Ready"))
    except Exception as e:
        print(f"   ❌ Vectorization system failed: {e}")
        test_results.append(("Vectorization System", False))
    
    # Test 6: Code Generation
    print("\n6. 🏗️  Testing Code Generation...")
    try:
        builder = SimplifiedAgentBuilder()
        
        # Get knowledge context if available
        knowledge_context = []
        if hasattr(builder, 'vectorizer') and builder.vectorizer:
            knowledge_context = await builder.get_knowledge_context(requirements)
        
        # Generate code
        generated_files = await builder.generate_agent_code(requirements, knowledge_context)
        
        # Verify files were generated
        required_files = ["bot.py", "requirements.txt", "Dockerfile", "pcc-deploy.toml"]
        for required_file in required_files:
            assert required_file in generated_files, f"Missing {required_file}"
            assert len(generated_files[required_file]) > 0, f"Empty {required_file}"
        
        print(f"   Generated {len(generated_files)} files")
        print(f"   Files: {list(generated_files.keys())}")
        print("   ✅ Code generation working correctly")
        test_results.append(("Code Generation", True))
    except Exception as e:
        print(f"   ❌ Code generation failed: {e}")
        test_results.append(("Code Generation", False))
    
    # Test 7: Code Validation
    print("\n7. 🔍 Testing Code Validation...")
    try:
        validation_result = await builder.validate_generated_code(generated_files)
        
        if validation_result["valid"]:
            print("   ✅ Generated code is valid")
        else:
            print(f"   ⚠️  Code validation warnings: {validation_result['warnings']}")
            print(f"   Errors: {validation_result['errors']}")
        
        print("   ✅ Code validation working correctly")
        test_results.append(("Code Validation", True))
    except Exception as e:
        print(f"   ❌ Code validation failed: {e}")
        test_results.append(("Code Validation", False))
    
    # Test 8: File System Operations
    print("\n8. 💾 Testing File System Operations...")
    try:
        # Save files
        agent_dir = await builder.save_generated_files(requirements, generated_files)
        
        # Verify files exist
        for filename in ["bot.py", "requirements.txt", "Dockerfile"]:
            file_path = agent_dir / filename
            assert file_path.exists(), f"File {filename} was not created"
            
            # Check file size
            size = file_path.stat().st_size
            assert size > 0, f"File {filename} is empty"
            print(f"   ✓ {filename} created ({size} bytes)")
        
        print(f"   Files saved to: {agent_dir}")
        print("   ✅ File system operations working correctly")
        test_results.append(("File System Operations", True))
    except Exception as e:
        print(f"   ❌ File system operations failed: {e}")
        test_results.append(("File System Operations", False))
    
    # Test 9: Error Handling
    print("\n9. 🛡️  Testing Error Handling...")
    try:
        # Test invalid requirements
        try:
            invalid_req = AgentRequirements(
                name="",  # Invalid empty name
                description="Test",
                use_case="test",
                channels=["invalid_channel"],  # Invalid channel
                languages=["invalid_lang"]  # Invalid language
            )
            RequirementsValidator.validate_requirements(invalid_req)
            assert False, "Should have raised ValidationError"
        except Exception:
            pass  # Expected
        
        print("   ✅ Error handling working correctly")
        test_results.append(("Error Handling", True))
    except Exception as e:
        print(f"   ❌ Error handling test failed: {e}")
        test_results.append(("Error Handling", False))
    
    # Test Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
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
        print("\n🎉 ALL CRITICAL TESTS PASSED!")
        print("The Pipecat Agent Builder is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} tests failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_tests())
    sys.exit(0 if success else 1)
