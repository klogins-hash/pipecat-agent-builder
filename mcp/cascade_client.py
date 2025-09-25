"""MCP client for Windsurf Cascade integration."""

import json
import asyncio
from typing import Dict, Any, List, Optional
import websockets
from dataclasses import dataclass, asdict

from core.config import AgentRequirements, settings
from core.logger import setup_logger

logger = setup_logger("mcp_cascade")


@dataclass
class MCPRequest:
    """MCP request structure."""
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None


@dataclass
class MCPResponse:
    """MCP response structure."""
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


class CascadeAgentGenerator:
    """Windsurf Cascade agent for generating Pipecat code."""
    
    def __init__(self):
        self.websocket = None
        self.request_id = 0
    
    async def connect(self) -> bool:
        """Connect to Windsurf Cascade via MCP."""
        try:
            logger.info(f"Connecting to Cascade at {settings.mcp_server_url}")
            self.websocket = await websockets.connect(settings.mcp_server_url)
            logger.info("Successfully connected to Windsurf Cascade")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Cascade: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Cascade."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
    
    async def _send_request(self, method: str, params: Dict[str, Any]) -> MCPResponse:
        """Send MCP request to Cascade."""
        if not self.websocket:
            raise ConnectionError("Not connected to Cascade")
        
        self.request_id += 1
        request = MCPRequest(
            method=method,
            params=params,
            id=str(self.request_id)
        )
        
        # Send request
        await self.websocket.send(json.dumps(asdict(request)))
        logger.debug(f"Sent MCP request: {method}")
        
        # Wait for response
        response_data = await self.websocket.recv()
        response_dict = json.loads(response_data)
        
        return MCPResponse(**response_dict)
    
    async def generate_pipecat_agent(
        self, 
        requirements: AgentRequirements,
        knowledge_context: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a complete Pipecat agent based on requirements."""
        
        params = {
            "task": "generate_pipecat_agent",
            "requirements": asdict(requirements),
            "knowledge_context": knowledge_context or [],
            "framework_info": {
                "name": "pipecat",
                "version": "latest",
                "documentation_base": "vectorized"
            }
        }
        
        logger.info(f"Requesting agent generation for: {requirements.name}")
        response = await self._send_request("generate_code", params)
        
        if response.error:
            raise Exception(f"Cascade error: {response.error}")
        
        return response.result
    
    async def validate_generated_code(self, code_files: Dict[str, str]) -> Dict[str, Any]:
        """Validate generated Pipecat code."""
        
        params = {
            "task": "validate_pipecat_code",
            "code_files": code_files,
            "validation_rules": [
                "syntax_check",
                "pipecat_imports",
                "pipeline_structure",
                "service_configuration",
                "deployment_readiness"
            ]
        }
        
        logger.info("Requesting code validation")
        response = await self._send_request("validate_code", params)
        
        if response.error:
            raise Exception(f"Validation error: {response.error}")
        
        return response.result
    
    async def optimize_agent_configuration(
        self, 
        requirements: AgentRequirements,
        performance_targets: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Get optimization recommendations for the agent."""
        
        params = {
            "task": "optimize_pipecat_agent",
            "requirements": asdict(requirements),
            "performance_targets": performance_targets or {
                "latency_target_ms": 800,
                "concurrent_users": 100,
                "cost_optimization": True
            }
        }
        
        logger.info("Requesting agent optimization")
        response = await self._send_request("optimize", params)
        
        if response.error:
            raise Exception(f"Optimization error: {response.error}")
        
        return response.result
    
    async def generate_deployment_config(
        self, 
        requirements: AgentRequirements,
        generated_code: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate deployment configuration for Pipecat Cloud."""
        
        params = {
            "task": "generate_deployment_config",
            "requirements": asdict(requirements),
            "code_files": generated_code,
            "target_platform": "pipecat_cloud",
            "deployment_settings": asdict(requirements.deployment)
        }
        
        logger.info("Requesting deployment configuration")
        response = await self._send_request("generate_deployment", params)
        
        if response.error:
            raise Exception(f"Deployment config error: {response.error}")
        
        return response.result
    
    async def create_knowledge_integration(
        self, 
        knowledge_sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate code for integrating knowledge sources."""
        
        params = {
            "task": "create_knowledge_integration",
            "knowledge_sources": knowledge_sources,
            "integration_patterns": [
                "rag_pipeline",
                "context_injection",
                "function_calling",
                "real_time_search"
            ]
        }
        
        logger.info(f"Requesting knowledge integration for {len(knowledge_sources)} sources")
        response = await self._send_request("integrate_knowledge", params)
        
        if response.error:
            raise Exception(f"Knowledge integration error: {response.error}")
        
        return response.result
    
    async def generate_test_suite(self, generated_code: Dict[str, str]) -> Dict[str, Any]:
        """Generate comprehensive test suite for the agent."""
        
        params = {
            "task": "generate_test_suite",
            "code_files": generated_code,
            "test_types": [
                "unit_tests",
                "integration_tests",
                "performance_tests",
                "conversation_tests"
            ]
        }
        
        logger.info("Requesting test suite generation")
        response = await self._send_request("generate_tests", params)
        
        if response.error:
            raise Exception(f"Test generation error: {response.error}")
        
        return response.result


class CascadeOrchestrator:
    """High-level orchestrator for Cascade operations."""
    
    def __init__(self):
        self.cascade = CascadeAgentGenerator()
        self.connected = False
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.connected = await self.cascade.connect()
        if not self.connected:
            raise ConnectionError("Failed to connect to Windsurf Cascade")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cascade.disconnect()
    
    async def build_complete_agent(
        self, 
        requirements: AgentRequirements,
        knowledge_context: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build a complete Pipecat agent with all components."""
        
        logger.info(f"Starting complete agent build for: {requirements.name}")
        
        # Step 1: Generate base agent code
        agent_result = await self.cascade.generate_pipecat_agent(
            requirements, knowledge_context
        )
        
        # Step 2: Optimize configuration
        optimization_result = await self.cascade.optimize_agent_configuration(requirements)
        
        # Step 3: Create knowledge integration if needed
        knowledge_result = None
        if requirements.knowledge_sources:
            knowledge_result = await self.cascade.create_knowledge_integration(
                [asdict(ks) for ks in requirements.knowledge_sources]
            )
        
        # Step 4: Generate deployment configuration
        deployment_result = await self.cascade.generate_deployment_config(
            requirements, agent_result.get("code_files", {})
        )
        
        # Step 5: Validate everything
        validation_result = await self.cascade.validate_generated_code(
            agent_result.get("code_files", {})
        )
        
        # Step 6: Generate test suite
        test_result = await self.cascade.generate_test_suite(
            agent_result.get("code_files", {})
        )
        
        return {
            "agent_code": agent_result,
            "optimization": optimization_result,
            "knowledge_integration": knowledge_result,
            "deployment_config": deployment_result,
            "validation": validation_result,
            "test_suite": test_result,
            "build_status": "complete"
        }
