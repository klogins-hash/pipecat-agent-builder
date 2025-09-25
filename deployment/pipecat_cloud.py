"""Pipecat Cloud deployment automation."""

import asyncio
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
import aiohttp
import docker
from docker.errors import DockerException

from core.config import AgentRequirements, settings
from core.logger import setup_logger

logger = setup_logger("pipecat_cloud")


class PipecatCloudDeployer:
    """Handle deployment to Pipecat Cloud."""
    
    def __init__(self):
        self.docker_client = None
        self.pipecat_api_base = "https://api.pipecat.daily.co/v1"
        
    async def deploy_agent(self, requirements: AgentRequirements, agent_dir: Path) -> Dict[str, Any]:
        """Deploy agent to Pipecat Cloud."""
        logger.info(f"Starting deployment of {requirements.name}")
        
        try:
            # Step 1: Initialize Docker client
            await self._init_docker()
            
            # Step 2: Build Docker image
            image_tag = await self._build_docker_image(requirements, agent_dir)
            
            # Step 3: Push to registry
            await self._push_docker_image(image_tag)
            
            # Step 4: Upload secrets
            await self._upload_secrets(requirements)
            
            # Step 5: Deploy to Pipecat Cloud
            deployment_result = await self._deploy_to_cloud(requirements, image_tag)
            
            logger.info("Deployment completed successfully")
            return {
                "status": "success",
                "image_tag": image_tag,
                "deployment_id": deployment_result.get("deployment_id"),
                "agent_url": deployment_result.get("agent_url")
            }
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _init_docker(self):
        """Initialize Docker client."""
        try:
            self.docker_client = docker.from_env()
            # Test Docker connection
            self.docker_client.ping()
            logger.info("Docker client initialized successfully")
        except DockerException as e:
            raise Exception(f"Docker not available or not running: {e}")
    
    async def _build_docker_image(self, requirements: AgentRequirements, agent_dir: Path) -> str:
        """Build Docker image for the agent."""
        agent_name = requirements.name.lower().replace(' ', '-').replace('_', '-')
        image_tag = f"{settings.docker_hub_username}/{agent_name}:latest"
        
        logger.info(f"Building Docker image: {image_tag}")
        
        try:
            # Build image
            image, build_logs = self.docker_client.images.build(
                path=str(agent_dir),
                tag=image_tag,
                rm=True,
                pull=True
            )
            
            # Log build output
            for log in build_logs:
                if 'stream' in log:
                    logger.debug(log['stream'].strip())
            
            logger.info(f"Docker image built successfully: {image_tag}")
            return image_tag
            
        except Exception as e:
            raise Exception(f"Docker build failed: {e}")
    
    async def _push_docker_image(self, image_tag: str):
        """Push Docker image to registry."""
        logger.info(f"Pushing Docker image: {image_tag}")
        
        try:
            # Login to Docker Hub if credentials provided
            if settings.docker_hub_username and settings.docker_hub_token:
                self.docker_client.login(
                    username=settings.docker_hub_username,
                    password=settings.docker_hub_token
                )
            
            # Push image
            push_logs = self.docker_client.images.push(
                image_tag,
                stream=True,
                decode=True
            )
            
            # Log push output
            for log in push_logs:
                if 'status' in log:
                    logger.debug(f"Push: {log['status']}")
                if 'error' in log:
                    raise Exception(f"Push error: {log['error']}")
            
            logger.info(f"Docker image pushed successfully: {image_tag}")
            
        except Exception as e:
            raise Exception(f"Docker push failed: {e}")
    
    async def _upload_secrets(self, requirements: AgentRequirements):
        """Upload secrets to Pipecat Cloud."""
        if not settings.pipecat_cloud_api_key:
            logger.warning("No Pipecat Cloud API key provided, skipping secrets upload")
            return
        
        secret_set_name = f"{requirements.name.lower().replace(' ', '-')}-secrets"
        
        # Prepare secrets
        secrets = {
            "OPENAI_API_KEY": settings.openai_api_key,
            "DEEPGRAM_API_KEY": settings.deepgram_api_key,
            "CARTESIA_API_KEY": settings.cartesia_api_key,
        }
        
        # Add optional secrets
        if settings.elevenlabs_api_key:
            secrets["ELEVENLABS_API_KEY"] = settings.elevenlabs_api_key
        if settings.daily_api_key:
            secrets["DAILY_API_KEY"] = settings.daily_api_key
        if settings.twilio_account_sid:
            secrets["TWILIO_ACCOUNT_SID"] = settings.twilio_account_sid
            secrets["TWILIO_AUTH_TOKEN"] = settings.twilio_auth_token
        
        # Filter out None values
        secrets = {k: v for k, v in secrets.items() if v is not None}
        
        logger.info(f"Uploading {len(secrets)} secrets to secret set: {secret_set_name}")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {settings.pipecat_cloud_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "secret_set_name": secret_set_name,
                    "secrets": secrets
                }
                
                async with session.post(
                    f"{self.pipecat_api_base}/secrets",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        logger.info("Secrets uploaded successfully")
                    else:
                        error_text = await response.text()
                        logger.warning(f"Secrets upload failed: {response.status} - {error_text}")
        
        except Exception as e:
            logger.warning(f"Failed to upload secrets: {e}")
    
    async def _deploy_to_cloud(self, requirements: AgentRequirements, image_tag: str) -> Dict[str, Any]:
        """Deploy agent to Pipecat Cloud."""
        if not settings.pipecat_cloud_api_key:
            raise Exception("Pipecat Cloud API key required for deployment")
        
        agent_name = requirements.name.lower().replace(' ', '-').replace('_', '-')
        secret_set_name = f"{agent_name}-secrets"
        
        deployment_config = {
            "agent_name": agent_name,
            "image": image_tag,
            "secret_set": secret_set_name,
            "scaling": {
                "min_agents": requirements.deployment.scaling_min,
                "max_agents": requirements.deployment.scaling_max
            },
            "environment": {
                "region": requirements.deployment.region,
                "environment": requirements.deployment.environment
            }
        }
        
        logger.info(f"Deploying agent with config: {deployment_config}")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {settings.pipecat_cloud_api_key}",
                    "Content-Type": "application/json"
                }
                
                async with session.post(
                    f"{self.pipecat_api_base}/agents",
                    headers=headers,
                    json=deployment_config
                ) as response:
                    
                    response_data = await response.json()
                    
                    if response.status == 200 or response.status == 201:
                        logger.info("Agent deployed successfully to Pipecat Cloud")
                        return response_data
                    else:
                        raise Exception(f"Deployment failed: {response.status} - {response_data}")
        
        except Exception as e:
            raise Exception(f"Pipecat Cloud deployment failed: {e}")
    
    async def get_deployment_status(self, agent_name: str) -> Dict[str, Any]:
        """Get deployment status from Pipecat Cloud."""
        if not settings.pipecat_cloud_api_key:
            raise Exception("Pipecat Cloud API key required")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {settings.pipecat_cloud_api_key}"
                }
                
                async with session.get(
                    f"{self.pipecat_api_base}/agents/{agent_name}",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"Status check failed: {response.status} - {error_text}")
        
        except Exception as e:
            raise Exception(f"Failed to get deployment status: {e}")
    
    async def _run_pcc_command(self, command: list, cwd: Path) -> Dict[str, Any]:
        """Run Pipecat Cloud CLI command."""
        try:
            logger.info(f"Running pcc command: {' '.join(command)}")
            
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            result = {
                "returncode": process.returncode,
                "stdout": stdout.decode(),
                "stderr": stderr.decode()
            }
            
            if process.returncode == 0:
                logger.info("PCC command completed successfully")
            else:
                logger.error(f"PCC command failed: {result['stderr']}")
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to run pcc command: {e}")


# Convenience functions
async def deploy_agent_to_cloud(requirements: AgentRequirements, agent_dir: Path) -> Dict[str, Any]:
    """Deploy an agent to Pipecat Cloud."""
    deployer = PipecatCloudDeployer()
    return await deployer.deploy_agent(requirements, agent_dir)


async def check_deployment_status(agent_name: str) -> Dict[str, Any]:
    """Check deployment status on Pipecat Cloud."""
    deployer = PipecatCloudDeployer()
    return await deployer.get_deployment_status(agent_name)
