from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import logging
import os
import traceback
import subprocess
import sys
from datetime import datetime, timedelta

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Semaphore to track if scraping is running
scraping_semaphore = asyncio.Lock()

async def run_scraping():
    try:
        async with scraping_semaphore:
            logger.info("Starting scrape_products task...")
            
            current_dir = os.path.dirname(os.path.dirname(__file__))
            script_path = os.path.join(current_dir, 'rohlikData', 'lmScrape.py')
            
            process = await asyncio.to_thread(subprocess.run,
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                cwd=current_dir
            )
            
            # Print stdout
            if process.stdout:
                print(process.stdout)
            
            # Only log as error if stderr contains actual error messages
            if process.stderr:
                if "ERROR:" in process.stderr:
                    logger.error(f"Errors: {process.stderr}")
                else:
                    logger.info(f"Script output: {process.stderr}")
                
            if process.returncode == 0:
                logger.info("Scrape_products task completed successfully")
            else:
                logger.error(f"Scraping failed with return code: {process.returncode}")
                
    except Exception as e:
        logger.error(f"ERROR in scrape_products: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

async def run_recipe_generation():
    try:
        if scraping_semaphore.locked():
            logger.info("Waiting for scraping to complete...")
            async with scraping_semaphore:
                pass
        
        logger.info("Starting recipe generation...")
        
        current_dir = os.path.dirname(os.path.dirname(__file__))
        script_path = os.path.join(current_dir, 'generateRec.py')
        
        # Use asyncio.to_thread here too
        process = await asyncio.to_thread(subprocess.run,
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=current_dir
        )
        
        print(process.stdout)
        
        if process.stderr:
            logger.error(f"Errors: {process.stderr}")
            
        if process.returncode == 0:
            logger.info("Recipe generation completed successfully")
        else:
            logger.error(f"Recipe generation failed with return code: {process.returncode}")
            
    except Exception as e:
        logger.error(f"Error during recipe generation: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

async def scheduled_scraping():
    await run_scraping()

async def scheduled_recipe_generation():
    await run_recipe_generation()

async def init_scheduler():
    scheduler = AsyncIOScheduler()
    
    # Add scheduled jobs
    scheduler.add_job(
        scheduled_scraping,
        'cron',
        minute='*/30',
        next_run_time=datetime.now() + timedelta(minutes=30)  # Start after 30 mins
    )
    
    scheduler.add_job(
        scheduled_recipe_generation,
        'cron',
        hour='*/2',
        next_run_time=datetime.now() + timedelta(hours=2)  # Start after 2 hours
    )
    
    scheduler.start()
    
    # Run initial tasks
    logger.info("Running initial scraping...")
    await run_scraping()
    
    logger.info("Running initial recipe generation...")
    await run_recipe_generation()
    
    return scheduler

# Function to use when importing the scheduler
def start_scheduler():
    """Use this function when importing the scheduler into another script"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    scheduler = loop.run_until_complete(init_scheduler())
    return scheduler

# For running as standalone script
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    scheduler = loop.run_until_complete(init_scheduler())
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()