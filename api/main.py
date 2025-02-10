from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.routes import products, recipes
from jobs.scheduler import init_scheduler
import os

# Initialize scheduler (but don't start it yet)
scheduler = init_scheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        # Shutdown scheduler on application shutdown
        scheduler.shutdown(wait=True)

app = FastAPI(
    title="Rohlik API",
    description="API for Rohlik product and recipe data",
    version="1.0.0",
    lifespan=lifespan
)

# Get allowed origins from environment variable or use default
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Configure CORS with environment variables
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(recipes.router, prefix="/api/v1", tags=["recipes"])

# No need for __main__ block anymore since we're using uvicorn directly