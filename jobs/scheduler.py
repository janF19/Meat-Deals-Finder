from apscheduler.schedulers.background import BackgroundScheduler
import logging
import os
import traceback
import subprocess
import sys

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def run_scraping():
    try:
        logger.info("Starting scrape_products task...")
        
        # Get the correct path for lmScrape.py (one level up, then into rohlikData)
        current_dir = os.path.dirname(os.path.dirname(__file__))
        script_path = os.path.join(current_dir, 'rohlikData', 'lmScrape.py')
        
        # Run with real-time output streaming
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=current_dir
        )
        
        # Stream output in real-time
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip())  # or logger.info(output.strip())
            if process.poll() is not None:
                break
            
        # Get any remaining output
        remaining_output, errors = process.communicate()
        if remaining_output:
            print(remaining_output.strip())
        if errors:
            logger.error(f"Errors: {errors}")
            
        if process.returncode == 0:
            logger.info("Scrape_products task completed successfully")
        else:
            logger.error(f"Scraping failed with return code: {process.returncode}")
            
    except Exception as e:
        logger.error(f"ERROR in scrape_products: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

def run_recipe_generation():
    try:
        logger.info("Starting recipe generation...")
        
        # Get the correct path for generateRec.py (one level up)
        current_dir = os.path.dirname(os.path.dirname(__file__))
        script_path = os.path.join(current_dir, 'generateRec.py')
        
        # Run with real-time output streaming
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=current_dir
        )
        
        # Stream output in real-time
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip())  # or logger.info(output.strip())
            if process.poll() is not None:
                break
            
        # Get any remaining output
        remaining_output, errors = process.communicate()
        if remaining_output:
            print(remaining_output.strip())
        if errors:
            logger.error(f"Errors: {errors}")
            
        if process.returncode == 0:
            logger.info("Recipe generation completed successfully")
        else:
            logger.error(f"Recipe generation failed with return code: {process.returncode}")
            
    except Exception as e:
        logger.error(f"Error during recipe generation: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

def init_scheduler():
    scheduler = BackgroundScheduler()
    
    # Run scraping every 30 minutes
    scheduler.add_job(
        run_scraping,
        'cron',
        minute='*/30'
    )
    
    # Run recipe generation every 2 hours
    scheduler.add_job(
        run_recipe_generation,
        'cron',
        hour='*/2'
    )
    
    scheduler.start()
    
    # Trigger first run immediately on startup
    logger.info("Running initial scraping and recipe generation...")
    run_scraping()
    run_recipe_generation()
    
    return scheduler