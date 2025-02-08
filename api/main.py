from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import products, recipes
import os

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