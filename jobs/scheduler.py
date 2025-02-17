from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from jobs.tasks import scrape_products, generate_recipes
import logging
from datetime import datetime

import logging

logger = logging.getLogger(__name__)

def init_scheduler():
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    scheduler = BackgroundScheduler()
    
    logger.info("Scheduling scraping job...")
    scheduler.add_job(
        scrape_products,
        trigger=CronTrigger(minute='*/15'),
        id='scrape_products',
        name='Scrape Rohlik products',
        max_instances=1,
        coalesce=True,
        misfire_grace_time=900
    )
    
    logger.info("Scheduling recipe job...")
    scheduler.add_job(
        generate_recipes,
        trigger=CronTrigger(minute='*/20'),
        id='generate_recipes',
        name='Generate recipes',
        max_instances=1,
        coalesce=True,
        misfire_grace_time=900
    )
    
    scheduler.start()
    logger.info(f"Scheduler started with jobs: {scheduler.get_jobs()}")
    
    logger.info("Forcing immediate job execution...")
    scheduler.get_job('scrape_products').modify(next_run_time=datetime.now())
    scheduler.get_job('generate_recipes').modify(next_run_time=datetime.now())
    
    return scheduler