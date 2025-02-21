from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.routes import products, recipes
from jobs.scheduler import init_scheduler
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Rohlik API",
    description="API for Rohlik product and recipe data",
    version="1.0.0"
)

# Initialize scheduler when app starts
scheduler = init_scheduler()

# Get allowed origins from environment variable or use default
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    if not scheduler or not scheduler.running:
        raise HTTPException(status_code=503, detail="Scheduler not running")
    return {"status": "healthy", "scheduler": "running"}

# Include routers
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(recipes.router, prefix="/api/v1", tags=["recipes"])

# No need for __main__ block anymore since we're using uvicorn directly