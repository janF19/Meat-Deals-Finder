
from api.main import app
from jobs.scheduler import init_scheduler
import uvicorn.server
import asyncio

async def main():
    # Initialize and start the scheduler
    scheduler = init_scheduler()
    scheduler.start()
    
    # Configure the uvicorn server
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    
    # Run the server
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())