

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import products, recipes

app = FastAPI(
    title="Rohlik API",
    description="API for Rohlik product and recipe data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(recipes.router, prefix="/api/v1", tags=["recipes"])