import pandas as pd
import requests
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from db_operations import DatabaseManager
from openai import OpenAI
from db_operations import DatabaseManager

def translate_food_names(df):
    """
    Translates Czech food names to generic English names using an LLM
    Returns DataFrame with added english_name column
    """
    try:
        # Initialize OpenAI client with API key from environment
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        def translate_single_name(name):
            prompt = f"""Translate this Czech food name to the most basic English ingredient name. 
            Return ONLY the main ingredient in 1-2 words maximum, nothing else.
            Examples: 
            'Vepřová krkovice v marinádě' -> 'pork'
            'Kuřecí prsní řízky' -> 'chicken'
            'Krůtí mletý polotovar' -> 'ground turkey'
            
            Czech name: {name}"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return response.choices[0].message.content.strip().lower()
        
        # Apply translation to each name
        df['english_name'] = df['Name'].apply(translate_single_name)
        return df
        
    except Exception as e:
        print(f"Error in translation: {e}")
        raise Exception(f"Error in translation: {e}")   


PANTRY_ITEMS = [
    # Basic staples
    "rice", "potato", "onion", "pepper", "salt",
    "olive oil", "vegetable oil", "flour", "butter",
    
    # Common spices
    "black pepper", "paprika", "cumin", "oregano", "thyme", "basil",
    
    # Common pantry items
    "pasta", "tomato sauce", "soy sauce", "vinegar", "sugar",
    
    # Common vegetables
    "onion",
    
    # Common condiments
    "mustard", "ketchup"
]

def get_recipes_for_ingredient(ingredient, english_ingredient, api_key):
    """
    Gets recipes that exactly match the main ingredient plus pantry items
    Limited to 1 recipe per ingredient
    """
    base_url = "https://api.spoonacular.com/recipes/findByIngredients"
    

    # Clean up the ingredient name further
    search_term = english_ingredient.split(',')[0]
    search_term = search_term.split('in')[0].strip()
    
    print(f"Searching recipes for: {ingredient} -> {english_ingredient} (searching as: {search_term})")
    
    params = {
        "apiKey": api_key,
        "ingredients": search_term,
        "number": 3,
        "ranking": 1,
        "ignorePantry": True
    }
    
    try:
        response = requests.get(base_url, params=params)
        recipes = response.json()
        
        exact_matches = []
        for recipe in recipes:
            used_ingredients = recipe.get('usedIngredients', [])
            
            # More flexible matching
            search_words = search_term.split()
            if any(all(word in ing['name'].lower() for word in search_words) 
                  for ing in used_ingredients):
                recipe_id = recipe['id']
                detail_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
                detail_response = requests.get(detail_url, params={"apiKey": api_key})
                recipe_details = detail_response.json()
                
                # Filter out pantry items from missing ingredients
                missing_ingredients = [
                    ing['name'] for ing in recipe.get('missedIngredients', [])
                    if ing.get('name') and not any(pantry_item in ing['name'].lower() 
                    for pantry_item in PANTRY_ITEMS)
                ]
                
                exact_matches.append({
                    'name': recipe['title'],
                    'ingredients': [ing['name'] for ing in used_ingredients],
                    'missing_ingredients': missing_ingredients,
                    'instructions': recipe_details.get('instructions', ''),
                    'cooking_time': recipe_details.get('readyInMinutes', 0),
                    'servings': recipe_details.get('servings', 0),
                    'source_url': recipe_details.get('sourceUrl', '')
                })
                
                if len(exact_matches) >= 2:
                    break
        
        print(f"Found {len(exact_matches)} recipes for {search_term}")
        return exact_matches
    
    except Exception as e:
        print(f"Error getting recipes for {ingredient}: {e}")
        return []

def main():
    load_dotenv()
    api_key = os.getenv("SPOONACULAR_API_KEY")
    if not api_key:
        raise ValueError("SPOONACULAR_API_KEY not found in environment variables")
    
    db_manager = DatabaseManager()
    
    # Get current products from database
    products_df = db_manager.get_products()
    
    # Create recipes dataframe
    all_recipes = []
    
    # Process each available product
    for _, row in products_df[products_df['is_available']].iterrows():
        # Get English translation for the product name
        english_name = translate_food_names(pd.DataFrame([{'Name': row['name']}]))['english_name'].iloc[0]
        
        # Get recipes for this product
        recipes = get_recipes_for_ingredient(row['name'], english_name, api_key)
        
        for recipe in recipes:
            all_recipes.append({
                'product': row['name'],
                'product_english': english_name,
                'recipe_name': recipe['name'],
                'cooking_time': recipe['cooking_time'],
                'servings': recipe['servings'],
                'instructions': recipe['instructions'],
                'recipe_url': recipe['source_url'],
                'missing_ingredients': recipe['missing_ingredients']
            })
    
    # Convert to DataFrame and update database
    if all_recipes:
        try:
            recipes_df = pd.DataFrame(all_recipes)
            db_manager.update_recipes(recipes_df)
            #db_manager.export_recipes_to_csv('recipes.csv')
        except Exception as e:
            print(f"Error updating recipes: {e}")
            raise Exception(f"Error updating recipes: {e}")
        

        print(f"\nUpdated database with {len(all_recipes)} recipe recommendations!")
    else:
        print("\nNo recipes found to update!")

if __name__ == "__main__":
    main()
