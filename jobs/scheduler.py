from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from jobs.tasks import scrape_products, generate_recipes
import logging

def init_scheduler():
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)  # More detailed logs
    scheduler = BackgroundScheduler()
    
    # Add print statements
    print("Scheduling scraping job...")
    scheduler.add_job(
        scrape_products,
        trigger=CronTrigger(hour='*/6'),
        id='scrape_products',
        name='Scrape Rohlik products'
    )
    
    print("Scheduling recipe job...")
    scheduler.add_job(
        generate_recipes,
        trigger=CronTrigger(hour='*/6', minute='15'),
        id='generate_recipes',
        name='Generate recipes'
    )
    
    scheduler.start()
    print("Scheduler started with jobs:", scheduler.get_jobs())
    return scheduler