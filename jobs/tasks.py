


import logging
from rohlikData.lmScrape import main as scrape_main
from generateRec import main as recipe_main

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_products():
    try:
        logger.info("Starting product scraping...")
        scrape_main()
        logger.info("Product scraping completed successfully")
    except Exception as e:
        logger.error(f"Error during product scraping: {str(e)}")

def generate_recipes():
    try:
        logger.info("Starting recipe generation...")
        recipe_main()
        logger.info("Recipe generation completed successfully")
    except Exception as e:
        logger.error(f"Error during recipe generation: {str(e)}")