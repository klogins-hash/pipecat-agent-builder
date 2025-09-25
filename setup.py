#!/usr/bin/env python3
"""Setup script for Pipecat Agent Builder."""

import asyncio
import sys
import subprocess
from pathlib import Path

from core.logger import setup_logger

logger = setup_logger("setup")


async def install_dependencies():
    """Install Python dependencies."""
    logger.info("Installing Python dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        logger.info("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False
    
    return True


async def setup_environment():
    """Set up environment configuration."""
    logger.info("Setting up environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        # Copy example to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        logger.info("Created .env file from .env.example")
        logger.info("Please edit .env file and add your API keys")
    elif env_file.exists():
        logger.info(".env file already exists")
    else:
        logger.warning("No .env.example file found")
    
    return True


async def create_directories():
    """Create necessary directories."""
    logger.info("Creating necessary directories...")
    
    directories = [
        "data/chroma_db",
        "generated_agents",
        "logs",
        "templates"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created directory: {dir_path}")
    
    logger.info("Directories created successfully")
    return True


async def check_docker():
    """Check if Docker is available."""
    logger.info("Checking Docker availability...")
    
    try:
        result = subprocess.run(
            ["docker", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        logger.info(f"Docker found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("Docker not found. Docker is required for deployment.")
        logger.info("Please install Docker from: https://www.docker.com/")
        return False


async def initialize_knowledge_base():
    """Initialize the knowledge base."""
    logger.info("Initializing knowledge base...")
    
    try:
        from knowledge.vectorizer import vectorize_pipecat_docs
        vectorizer = await vectorize_pipecat_docs()
        stats = vectorizer.get_stats()
        logger.info(f"Knowledge base initialized with {stats['total_chunks']} chunks")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize knowledge base: {e}")
        return False


async def run_setup():
    """Run the complete setup process."""
    logger.info("Starting Pipecat Agent Builder setup...")
    
    steps = [
        ("Installing dependencies", install_dependencies),
        ("Setting up environment", setup_environment),
        ("Creating directories", create_directories),
        ("Checking Docker", check_docker),
        ("Initializing knowledge base", initialize_knowledge_base),
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        logger.info(f"Step: {step_name}")
        try:
            success = await step_func()
            if success:
                success_count += 1
                logger.info(f"✅ {step_name} completed")
            else:
                logger.warning(f"⚠️  {step_name} completed with warnings")
        except Exception as e:
            logger.error(f"❌ {step_name} failed: {e}")
    
    logger.info(f"Setup completed: {success_count}/{len(steps)} steps successful")
    
    if success_count == len(steps):
        logger.info("🎉 Setup completed successfully!")
        logger.info("Run 'python main.py' to start building agents")
    else:
        logger.warning("⚠️  Setup completed with some issues")
        logger.info("Check the logs above and resolve any issues before running")
    
    return success_count == len(steps)


if __name__ == "__main__":
    asyncio.run(run_setup())
