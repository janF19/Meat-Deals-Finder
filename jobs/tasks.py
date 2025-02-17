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