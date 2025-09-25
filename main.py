#!/usr/bin/env python3
"""
Pipecat Agent Builder - Main Application

An LLM-powered conversational interface for building and deploying Pipecat AI agents.
"""

import asyncio
import sys
import uuid
from pathlib import Path
from typing import Optional
import signal

from core.config import settings
from core.logger import setup_logger
from core.exceptions import *
from core.validators import RequirementsValidator, APIKeyValidator, ResourceValidator
from core.monitoring import metrics_collector, PerformanceMonitor, HealthChecker, start_session, end_session
from knowledge.vectorizer import vectorize_pipecat_docs, PipecatDocumentationVectorizer
from interface.conversation import gather_agent_requirements
from mcp.cascade_client import CascadeOrchestrator
from generation.templates import PipecatTemplateGenerator
from deployment.pipecat_cloud import PipecatCloudDeployer

logger = setup_logger("main")


class PipecatAgentBuilder:
    """Main application class for building Pipecat agents."""
    
    def __init__(self):
        self.vectorizer: Optional[PipecatDocumentationVectorizer] = None
        self.template_generator = PipecatTemplateGenerator()
        self.deployer = PipecatCloudDeployer()
        self.performance_monitor = PerformanceMonitor(metrics_collector)
        self.health_checker = HealthChecker(metrics_collector)
        self.shutdown_event = asyncio.Event()
        
        # Setup health checks
        self._setup_health_checks()
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
    def _setup_health_checks(self):
        """Setup application health checks."""
        
        def check_vectorizer_health():
            if not self.vectorizer:
                return {"healthy": False, "reason": "Vectorizer not initialized"}
            
            try:
                stats = self.vectorizer.get_stats()
                return {
                    "healthy": stats["total_chunks"] > 0,
                    "chunks": stats["total_chunks"],
                    "reason": "No documentation chunks" if stats["total_chunks"] == 0 else "OK"
                }
            except Exception as e:
                return {"healthy": False, "reason": f"Vectorizer error: {e}"}
        
        def check_api_keys():
            key_status = APIKeyValidator.validate_api_keys(settings)
            missing_keys = [k for k, v in key_status.items() if not v]
            
            return {
                "healthy": len(missing_keys) == 0,
                "missing_keys": missing_keys,
                "reason": f"Missing keys: {missing_keys}" if missing_keys else "OK"
            }
        
        def check_disk_space():
            try:
                import shutil
                total, used, free = shutil.disk_usage(Path.cwd())
                free_gb = free / (1024**3)
                
                return {
                    "healthy": free_gb > 1.0,  # Need at least 1GB free
                    "free_gb": round(free_gb, 2),
                    "reason": "Low disk space" if free_gb <= 1.0 else "OK"
                }
            except Exception as e:
                return {"healthy": False, "reason": f"Disk check failed: {e}"}
        
        self.health_checker.register_health_check("vectorizer", check_vectorizer_health)
        self.health_checker.register_health_check("api_keys", check_api_keys)
        self.health_checker.register_health_check("disk_space", check_disk_space)
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers."""
        
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    async def initialize(self):
        """Initialize the agent builder with comprehensive error handling."""
        logger.info("Initializing Pipecat Agent Builder...")
        
        try:
            # Validate configuration
            await self._validate_configuration()
            
            # Initialize vectorizer with retry logic
            await self._initialize_vectorizer_with_retry()
            
            # Start background monitoring
            asyncio.create_task(self.performance_monitor.start_monitoring())
            
            # Run initial health check
            health_status = await self.health_checker.run_health_checks()
            if not health_status["overall"]["healthy"]:
                logger.warning("Some health checks failed:")
                for check, result in health_status.items():
                    if check != "overall" and not result["healthy"]:
                        logger.warning(f"  {check}: {result.get('reason', 'Unknown error')}")
            
            logger.info("Pipecat Agent Builder initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pipecat Agent Builder: {e}")
            raise ConfigurationError(f"Initialization failed: {e}")
    
    async def _validate_configuration(self):
        """Validate system configuration."""
        logger.info("Validating configuration...")
        
        # Check API keys
        key_status = APIKeyValidator.validate_api_keys(settings)
        missing_keys = [k for k, v in key_status.items() if not v]
        
        if missing_keys:
            raise APIKeyError(f"Missing or invalid API keys: {missing_keys}")
        
        # Check required directories
        required_dirs = [
            Path(settings.chroma_persist_directory),
            Path(settings.output_path),
            Path("logs")
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logger.debug(f"Created directory: {dir_path}")
                except Exception as e:
                    raise ConfigurationError(f"Cannot create directory {dir_path}: {e}")
        
        # Check documentation path
        docs_path = Path(settings.docs_path)
        if not docs_path.exists():
            raise ConfigurationError(f"Documentation path not found: {docs_path}")
        
        logger.info("Configuration validation completed")
    
    async def _initialize_vectorizer_with_retry(self, max_retries: int = 3):
        """Initialize vectorizer with retry logic."""
        logger.info("Initializing vectorizer...")
        
        for attempt in range(max_retries):
            try:
                self.vectorizer = PipecatDocumentationVectorizer()
                stats = self.vectorizer.get_stats()
                
                if stats["total_chunks"] == 0:
                    logger.info("No vectorized documentation found. Starting vectorization...")
                    await self._vectorize_documentation()
                else:
                    logger.info(f"Found {stats['total_chunks']} vectorized documentation chunks")
                
                return  # Success
                
            except Exception as e:
                logger.error(f"Vectorizer initialization attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    raise VectorizationError(f"Failed to initialize vectorizer after {max_retries} attempts: {e}")
                
                # Wait before retry
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def _vectorize_documentation(self):
        """Vectorize the Pipecat documentation."""
        logger.info("Vectorizing Pipecat documentation...")
        self.vectorizer = await vectorize_pipecat_docs()
        logger.info("Documentation vectorization complete")
    
    async def build_agent_interactive(self):
        """Build an agent through interactive conversation with comprehensive error handling."""
        session_id = str(uuid.uuid4())
        session = start_session(session_id)
        
        try:
            logger.info("Starting interactive agent building process...")
            
            # Step 1: Gather requirements through conversation
            logger.info("🗣️  Starting requirements gathering conversation...")
            self._print_welcome_banner()
            
            try:
                requirements = await gather_agent_requirements()
                logger.info(f"Requirements gathered for agent: {requirements.name}")
                
                # Validate requirements
                requirements = RequirementsValidator.validate_requirements(requirements)
                
                # Check resource limits
                ResourceValidator.validate_resource_limits(requirements)
                
                # Get resource estimates
                resource_estimate = ResourceValidator.estimate_resource_usage(requirements)
                logger.info(f"Agent complexity: {resource_estimate['complexity_score']}")
                
                session.agent_name = requirements.name
                session.use_case = requirements.use_case
                metrics_collector.record_session_metric(session_id, "complexity", resource_estimate['complexity_score'])
                
            except ConversationError as e:
                logger.error(f"Conversation failed: {e}")
                end_session(session_id, "failed", str(e))
                raise
            except ValidationError as e:
                logger.error(f"Requirements validation failed: {e}")
                end_session(session_id, "failed", str(e))
                print(f"\n❌ Invalid requirements: {e}")
                return
            
            # Step 2: Search knowledge base for relevant patterns
            logger.info("🔍 Searching knowledge base for relevant patterns...")
            try:
                knowledge_context = await self._get_knowledge_context(requirements)
                metrics_collector.record_session_metric(session_id, "knowledge_chunks", len(knowledge_context))
            except Exception as e:
                logger.warning(f"Knowledge search failed, continuing without context: {e}")
                knowledge_context = []
            
            # Step 3: Generate code using Windsurf Cascade or templates
            logger.info("🤖 Generating agent code...")
            try:
                generated_files = await self._generate_agent_code_with_fallback(requirements, knowledge_context)
                metrics_collector.record_session_metric(session_id, "files_generated", len(generated_files))
            except CodeGenerationError as e:
                logger.error(f"Code generation failed: {e}")
                end_session(session_id, "failed", str(e))
                print(f"\n❌ Code generation failed: {e}")
                return
            
            # Step 4: Validate generated code
            logger.info("🔍 Validating generated code...")
            try:
                validation_result = await self._validate_generated_code(generated_files)
                if not validation_result["valid"]:
                    logger.warning(f"Code validation warnings: {validation_result['warnings']}")
            except Exception as e:
                logger.warning(f"Code validation failed: {e}")
            
            # Step 5: Save generated files
            logger.info("💾 Saving generated files...")
            try:
                agent_dir = await self._save_generated_files(requirements, generated_files)
            except Exception as e:
                logger.error(f"Failed to save files: {e}")
                end_session(session_id, "failed", str(e))
                raise
            
            # Step 6: Optional deployment
            deploy_choice = await self._prompt_for_deployment()
            deployment_result = None
            
            if deploy_choice:
                logger.info("🌟 Deploying to Pipecat Cloud...")
                try:
                    deployment_result = await self._deploy_agent_with_retry(requirements, agent_dir)
                    logger.info(f"Deployment complete: {deployment_result}")
                    metrics_collector.record_session_metric(session_id, "deployed", True)
                except DeploymentError as e:
                    logger.error(f"Deployment failed: {e}")
                    print(f"\n⚠️  Deployment failed: {e}")
                    print("Your agent files are still available locally for manual deployment.")
                    metrics_collector.record_session_metric(session_id, "deployment_failed", True)
            
            # Step 7: Show summary
            await self._show_build_summary(requirements, agent_dir, deployment_result)
            
            # Mark session as completed
            end_session(session_id, "completed")
            
        except KeyboardInterrupt:
            logger.info("Build process interrupted by user")
            end_session(session_id, "interrupted", "User interrupted")
            print("\n\n👋 Build process cancelled by user.")
            
        except Exception as e:
            logger.error(f"Unexpected error during agent building: {e}")
            end_session(session_id, "failed", str(e))
            print(f"\n❌ An unexpected error occurred: {e}")
            print("Please check the logs for more details.")
            raise
    
    def _print_welcome_banner(self):
        """Print welcome banner with system status."""
        print("\n" + "="*60)
        print("🎯 PIPECAT AGENT BUILDER")
        print("="*60)
        print("Let's build your AI agent through conversation!")
        print("Open http://localhost:7860 in your browser to start talking.")
        
        # Show system status
        if self.vectorizer:
            stats = self.vectorizer.get_stats()
            print(f"📚 Knowledge Base: {stats['total_chunks']} documentation chunks ready")
        
        print("="*60 + "\n")
    
    async def _prompt_for_deployment(self) -> bool:
        """Prompt user for deployment with timeout."""
        try:
            # Use asyncio to add timeout to input
            loop = asyncio.get_event_loop()
            
            def get_input():
                return input("\n🚀 Deploy to Pipecat Cloud? (y/n): ").lower().strip()
            
            # Wait for input with 30 second timeout
            try:
                choice = await asyncio.wait_for(
                    loop.run_in_executor(None, get_input),
                    timeout=30.0
                )
                return choice == 'y'
            except asyncio.TimeoutError:
                print("\nNo response received, skipping deployment.")
                return False
                
        except Exception as e:
            logger.warning(f"Error getting deployment choice: {e}")
            return False
    
    async def _get_knowledge_context(self, requirements) -> list:
        """Get relevant knowledge context from vectorized documentation."""
        if not self.vectorizer:
            return []
        
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
    
    async def _generate_agent_code_with_fallback(self, requirements, knowledge_context) -> dict:
        """Generate agent code using Windsurf Cascade with template fallback."""
        
        # Try to use Windsurf Cascade first
        try:
            async with CascadeOrchestrator() as cascade:
                logger.info("Using Windsurf Cascade for advanced code generation...")
                result = await cascade.build_complete_agent(requirements, knowledge_context)
                generated_files = result.get("agent_code", {}).get("code_files", {})
                
                if not generated_files:
                    raise CodeGenerationError("Cascade returned empty result")
                
                logger.info(f"Cascade generated {len(generated_files)} files")
                return generated_files
                
        except MCPConnectionError as e:
            logger.warning(f"Cascade connection failed, using templates: {e}")
        except Exception as e:
            logger.warning(f"Cascade generation failed, falling back to templates: {e}")
        
        # Fallback to template generation
        logger.info("Using template-based code generation...")
        try:
            generated_files = self.template_generator.generate_agent_files(requirements)
            
            if not generated_files:
                raise CodeGenerationError("Template generation returned empty result")
            
            logger.info(f"Templates generated {len(generated_files)} files")
            return generated_files
            
        except Exception as e:
            raise CodeGenerationError(f"Both Cascade and template generation failed: {e}")
    
    async def _validate_generated_code(self, generated_files: dict) -> dict:
        """Validate generated code for syntax and completeness."""
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
                logger.debug("bot.py syntax validation passed")
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
        
        # Validate requirements.txt format
        if "requirements.txt" in generated_files:
            req_content = generated_files["requirements.txt"]
            if "pipecat-ai" not in req_content:
                validation_result["warnings"].append("Missing pipecat-ai dependency")
        
        return validation_result
    
    async def _deploy_agent_with_retry(self, requirements, agent_dir: Path, max_retries: int = 2):
        """Deploy agent with retry logic."""
        
        for attempt in range(max_retries):
            try:
                deployment_result = await self.deployer.deploy_agent(requirements, agent_dir)
                
                if deployment_result.get("status") == "success":
                    return deployment_result
                else:
                    raise DeploymentError(f"Deployment failed: {deployment_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Deployment attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    raise DeploymentError(f"Deployment failed after {max_retries} attempts: {e}")
                
                # Wait before retry
                await asyncio.sleep(5)
    
    async def _show_build_summary(self, requirements, agent_dir: Path, deployment_result):
        """Show comprehensive build summary."""
        print("\n" + "="*60)
        print("🎉 AGENT BUILD COMPLETE!")
        print("="*60)
        print(f"Agent Name: {requirements.name}")
        print(f"Description: {requirements.description}")
        print(f"Use Case: {requirements.use_case}")
        print(f"Channels: {', '.join(requirements.channels)}")
        print(f"Languages: {', '.join(requirements.languages)}")
        print(f"Files Location: {agent_dir}")
        
        # Show resource estimates
        resource_estimate = ResourceValidator.estimate_resource_usage(requirements)
        print(f"\n📊 Resource Estimates:")
        print(f"  Complexity: {resource_estimate['complexity_score']}")
        print(f"  CPU Units: {resource_estimate['estimated_cpu_units']}")
        print(f"  Memory: {resource_estimate['estimated_memory_mb']} MB")
        print(f"  Storage: {resource_estimate['estimated_storage_mb']} MB")
        
        if deployment_result and deployment_result.get("status") == "success":
            print("\n🌟 Deployment Status: DEPLOYED")
            print("Your agent is now live on Pipecat Cloud!")
            if "agent_url" in deployment_result:
                print(f"Agent URL: {deployment_result['agent_url']}")
        else:
            print("\n📋 Next Steps:")
            print(f"1. Review generated files in: {agent_dir}")
            print("2. Add your API keys to .env file")
            print("3. Test locally: python bot.py")
            print("4. Deploy: pcc deploy")
        
        # Show service compatibility warnings
        warnings = APIKeyValidator.validate_service_compatibility(requirements)
        if warnings:
            print("\n⚠️  Service Compatibility Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        
        print("="*60 + "\n")
    
    async def _save_generated_files(self, requirements, generated_files) -> Path:
        """Save generated files to disk."""
        agent_name = requirements.name.lower().replace(' ', '_').replace('-', '_')
        agent_dir = Path(settings.output_path) / agent_name
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        for filename, content in generated_files.items():
            file_path = agent_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.debug(f"Saved {filename}")
        
        logger.info(f"Generated agent saved to: {agent_dir}")
        return agent_dir
    
    async def _deploy_agent(self, requirements, agent_dir: Path):
        """Deploy agent to Pipecat Cloud."""
        return await self.deployer.deploy_agent(requirements, agent_dir)
    
    async def _show_build_summary(self, requirements, agent_dir: Path, deployed: bool):
        """Show build summary to user."""
        print("\n" + "="*60)
        print("🎉 AGENT BUILD COMPLETE!")
        print("="*60)
        print(f"Agent Name: {requirements.name}")
        print(f"Description: {requirements.description}")
        print(f"Use Case: {requirements.use_case}")
        print(f"Channels: {', '.join(requirements.channels)}")
        print(f"Languages: {', '.join(requirements.languages)}")
        print(f"Files Location: {agent_dir}")
        
        if deployed:
            print("\n🌟 Deployment Status: DEPLOYED")
            print("Your agent is now live on Pipecat Cloud!")
        else:
            print("\n📋 Next Steps:")
            print(f"1. Review generated files in: {agent_dir}")
            print("2. Add your API keys to .env file")
            print("3. Test locally: python bot.py")
            print("4. Deploy: pcc deploy")
        
        print("="*60 + "\n")


async def main():
    """Main application entry point."""
    logger.info("Starting Pipecat Agent Builder")
    
    # Check required API keys
    required_keys = ["openai_api_key", "deepgram_api_key", "cartesia_api_key"]
    missing_keys = [key for key in required_keys if not getattr(settings, key)]
    
    if missing_keys:
        logger.error(f"Missing required API keys: {missing_keys}")
        print("\n❌ Missing required API keys!")
        print("Please set the following environment variables:")
        for key in missing_keys:
            print(f"  - {key.upper()}")
        print("\nCopy .env.example to .env and add your API keys.")
        sys.exit(1)
    
    try:
        # Initialize the builder
        builder = PipecatAgentBuilder()
        await builder.initialize()
        
        # Start interactive building process
        await builder.build_agent_interactive()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
