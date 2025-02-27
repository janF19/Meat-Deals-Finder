from fastapi import APIRouter, HTTPException
from db_operations import DatabaseManager
from typing import List, Optional
from pydantic import BaseModel
from datetime import date

router = APIRouter()

class Product(BaseModel):
    id: Optional[int] = None
    name: str
    current_price: float
    original_price: float
    discount: str
    weight: float
    price_per_kg: float
    expiry_date: Optional[date] = None
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
    if expiring_soon and 'expiry_date' in products.columns:
        current_date = date.today()
        products = products[products['expiry_date'].notna() & (products['expiry_date'] <= current_date)]
    
    # Convert DataFrame to list of dictionaries and handle None values
    product_list = []
    for _, row in products.iterrows():
        product_dict = row.to_dict()
        # Convert None to proper types for validation
        if product_dict.get('expiry_date') is None:
            product_dict['expiry_date'] = None
        if product_dict.get('id') is None:
            product_dict['id'] = None
        product_list.append(product_dict)
    
    return product_list

@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    db = DatabaseManager()
    products = db.get_products()
    product = products[products['id'] == product_id]
    
    if product.empty:
        raise HTTPException(status_code=404, detail="Product not found")
        
    return product.iloc[0].to_dict()