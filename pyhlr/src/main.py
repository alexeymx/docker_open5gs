import asyncio
import logging
from src.hlr.server import GSUPServer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the HLR service."""
    server = GSUPServer()
    
    try:
        logger.info("Starting HLR service...")
        await server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down HLR service...")
    except Exception as e:
        logger.error(f"Error running HLR service: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 