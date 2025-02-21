import logging
from rohlikData.lmScrape import main as scrape_main
from generateRec import main as recipe_main
import os
import traceback
import asyncio
import sys

# Add this at the top of the file
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def scrape_products():
    try:
        logger.info("Starting scrape_products task...")
        logger.info(f"Current directory: {os.getcwd()}")
        
        # Check if Playwright is installed
        try:
            from playwright.sync_api import sync_playwright
            logger.info("Playwright is properly imported")
        except Exception as e:
            logger.error(f"Playwright import error: {str(e)}")
            logger.error("Try running: poetry run playwright install")
            return
        
        # Check if necessary files exist
        required_files = ['rohlikData/lmScrape.py', 'db_operations.py']
        for file in required_files:
            if os.path.exists(file):
                logger.info(f"File exists: {file}")
            else:
                logger.error(f"Missing file: {file}")
                return
        
        scrape_main()
        logger.info("Scrape_products task completed")
    except Exception as e:
        logger.error(f"ERROR in scrape_products: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

def generate_recipes():
    try:
        logger.info("Starting recipe generation...")
        logger.debug("Initializing recipe_main...")
        
        # Add error handling for recipe generation
        try:
            result = recipe_main()
            if result:
                logger.info(f"Recipe generation completed with result: {result}")
            else:
                logger.warning("Recipe generation completed but no results returned")
        except Exception as recipe_error:
            logger.error(f"Error in recipe_main: {str(recipe_error)}")
            logger.error(f"Recipe error traceback: {traceback.format_exc()}")
            raise
            
    except Exception as e:
        logger.error(f"Error during recipe generation: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")