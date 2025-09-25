#!/usr/bin/env python3
"""Script to vectorize Pipecat documentation."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge.vectorizer import vectorize_pipecat_docs
from core.logger import setup_logger

logger = setup_logger("vectorize_script")


async def main():
    """Main function to vectorize documentation."""
    logger.info("Starting Pipecat documentation vectorization...")
    
    try:
        vectorizer = await vectorize_pipecat_docs()
        stats = vectorizer.get_stats()
        
        logger.info("Vectorization completed successfully!")
        logger.info(f"Statistics: {stats}")
        
        # Test search functionality
        logger.info("Testing search functionality...")
        results = await vectorizer.search("voice assistant pipeline", n_results=3)
        
        logger.info(f"Search test returned {len(results)} results")
        for i, result in enumerate(results):
            logger.info(f"Result {i+1}: {result['metadata'].get('source_file', 'Unknown')} "
                       f"(distance: {result.get('distance', 'N/A')})")
        
    except Exception as e:
        logger.error(f"Error during vectorization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
