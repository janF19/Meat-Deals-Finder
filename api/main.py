from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import products, recipes
from jobs.scheduler import init_scheduler
import uvicorn
import os
import asyncio

app = FastAPI(
    title="Rohlik API",
    description="API for Rohlik product and recipe data",
    version="1.0.0"
)

# Get allowed origins from environment variable or use default
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Configure CORS with environment variables
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Now configurable via environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(recipes.router, prefix="/api/v1", tags=["recipes"])

async def start_app():
    # Initialize and start the scheduler
    scheduler = init_scheduler()
    scheduler.start()
    
    # Configure the uvicorn server
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    
    # Run the server
    await server.serve()

if __name__ == "__main__":
    asyncio.run(start_app())