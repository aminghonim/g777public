import logging
import asyncio
from .ai_engine import AIEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting G777 Researcher Mission...")
    engine = AIEngine()
    
    task = "ابحث عن أحدث أسعار العقارات في التجمع الخامس"
    logger.info(f"Task: {task}")
    
    try:
        response = await engine.generate_response(task, "SYSTEM_ADMIN")
        logger.info(f"Mission Result: {response}")
    except Exception as e:
        logger.error(f"Mission Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
