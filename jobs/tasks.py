import logging
from rohlikData.lmScrape import main as scrape_main
from generateRec import main as recipe_main
import os
import traceback

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def scrape_products():
    try:
        print("Starting scrape_products task...")
        print(f"Current directory: {os.getcwd()}")
        print(f"Environment variables: {os.environ}")
        scrape_main()
        print("Scrape_products task completed")
    except Exception as e:
        print(f"ERROR in scrape_products: {str(e)}")
        traceback.print_exc()

def generate_recipes():
    try:
        logger.info("Starting recipe generation...")
        logger.debug("Initializing recipe_main...")
        recipe_main()
        logger.info("Recipe generation completed successfully")
    except Exception as e:
        logger.error(f"Error during recipe generation: {str(e)}", exc_info=True)