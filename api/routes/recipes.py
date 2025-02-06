

from fastapi import APIRouter, HTTPException
from db_operations import DatabaseManager
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class Recipe(BaseModel):
    id: int
    product: str
    product_english: str
    recipe_name: str
    cooking_time: int
    servings: int
    instructions: str
    recipe_url: str
    missing_ingredients: List[str]

@router.get("/recipes", response_model=List[Recipe])
async def get_recipes(product_name: Optional[str] = None):
    db = DatabaseManager()
    recipes = db.get_recipes()
    
    if product_name:
        recipes = recipes[recipes['product'].str.contains(product_name, case=False)]
        
    return recipes.to_dict('records')

@router.get("/recipes/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: int):
    db = DatabaseManager()
    recipes = db.get_recipes()
    recipe = recipes[recipes['id'] == recipe_id]
    
    if recipe.empty:
        raise HTTPException(status_code=404, detail="Recipe not found")
        
    return recipe.iloc[0].to_dict()