

import uvicorn
from api.main import app
from jobs.scheduler import init_scheduler

if __name__ == "__main__":
    # Initialize and start the scheduler
    scheduler = init_scheduler()
    scheduler.start()
    
    # Run the FastAPI application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )