from fastapi import APIRouter, HTTPException
from db_operations import DatabaseManager
from typing import List, Optional
from pydantic import BaseModel
from datetime import date

router = APIRouter()

class Product(BaseModel):
    id: int
    name: str
    current_price: float
    original_price: float
    discount: str
    weight: float
    price_per_kg: float
    expiry_date: date
    is_available: bool

@router.get("/products", response_model=List[Product])
async def get_products(
    available_only: bool = False,
    expiring_soon: bool = False
):
    db = DatabaseManager()
    products = db.get_products()
    
    if available_only:
        products = products[products['is_available']]
    if expiring_soon:
        products = products[products['expiry_date'] <= date.today()]
        
    return products.to_dict('records')

@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    db = DatabaseManager()
    products = db.get_products()
    product = products[products['id'] == product_id]
    
    if product.empty:
        raise HTTPException(status_code=404, detail="Product not found")
        
    return product.iloc[0].to_dict()