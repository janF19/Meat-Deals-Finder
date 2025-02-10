from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from jobs.tasks import scrape_products, generate_recipes

def init_scheduler():
    scheduler = BackgroundScheduler()
    
    # Schedule product scraping every 6 hours
    scheduler.add_job(
        scrape_products,
        trigger=CronTrigger(hour='*/6'),
        id='scrape_products',
        name='Scrape Rohlik products'
    )
    
    # Schedule recipe generation 15 minutes after each scraping
    scheduler.add_job(
        generate_recipes,
        trigger=CronTrigger(hour='*/6', minute='15'),
        id='generate_recipes',
        name='Generate recipes'
    )
    
    # Start the scheduler
    scheduler.start()
    
    return scheduler