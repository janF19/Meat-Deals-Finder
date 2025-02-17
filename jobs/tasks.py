import logging
from rohlikData.lmScrape import main as scrape_main
from generateRec import main as recipe_main
import os
import traceback
import logging  

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def scrape_products():
    try:
        logger.info("Starting scrape_products task...")
        logger.info(f"Current directory: {os.getcwd()}")
        logger.info(f"Environment variables: {dict(os.environ)}")  # Log environment variables
        
        # Check if necessary files exist
        required_files = ['rohlikData/lmScrape.py', 'db_operations.py']
        for file in required_files:
            if os.path.exists(file):
                logger.info(f"File exists: {file}")
            else:
                logger.error(f"Missing file: {file}")
        
        scrape_main()
        logger.info("Scrape_products task completed")
    except Exception as e:
        logger.error(f"ERROR in scrape_products: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

def generate_recipes():
    try:
        logger.info("Starting recipe generation...")
        logger.debug("Initializing recipe_main...")
        recipe_main()
        logger.info("Recipe generation completed successfully")
    except Exception as e:
        logger.error(f"Error during recipe generation: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")