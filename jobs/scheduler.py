from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from jobs.tasks import scrape_products, generate_recipes
import logging

def init_scheduler():
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    scheduler = BackgroundScheduler()
    
    print("Scheduling scraping job...")
    # Run every hour instead of every 6 hours for testing
    scheduler.add_job(
        scrape_products,
        trigger=CronTrigger(minute='*/10'),  # Run every minute for testing
        id='scrape_products',
        name='Scrape Rohlik products',
        max_instances=1,
        coalesce=True  # Combine missed runs
    )
    
    print("Scheduling recipe job...")
    scheduler.add_job(
        generate_recipes,
        trigger=CronTrigger(minute='*/12'),  # Run every 2 minutes for testing
        id='generate_recipes',
        name='Generate recipes',
        max_instances=1,
        coalesce=True
    )
    
    scheduler.start()
    print("Scheduler started with jobs:", scheduler.get_jobs())
    
    # Force run jobs immediately for testing
    scheduler.get_job('scrape_products').modify(next_run_time=None)
    scheduler.get_job('generate_recipes').modify(next_run_time=None)
    
    return scheduler