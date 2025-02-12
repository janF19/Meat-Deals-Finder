import os
import agentql
from playwright.sync_api import sync_playwright
import dotenv
from datetime import datetime, timedelta
import re
import sys
import pandas as pd 
import traceback

# Add parent directory to Python path (place this before the import)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


# Now we can import DatabaseManager
from db_operations import DatabaseManager

dotenv.load_dotenv()

PRODUCTS_URL = "https://www.rohlik.cz/zachran-a-usetri/c300103000-maso-a-ryby/"

COOKIE_QUERY = """
{
    cookies_form {
        reject_btn
    }
}
"""

PRODUCT_QUERY = """
{
    products[] {
        name
        current_price
        original_price
        discount
        weight
        price_per_kg
        expiry_date
        is_available
    }
}
"""

def process_expiry_date(expiry_date_str, current_date):
    if expiry_date_str == "Spotřebujte zítra":
        next_day = datetime.strptime(current_date, '%Y-%m-%d') + timedelta(days=1)
        return next_day.strftime('%Y-%m-%d')
    elif "Spotřeba do" in expiry_date_str:
        # Fix the date parsing
        match = re.search(r'do (\d+)\. (\d+)\.', expiry_date_str)
        if match:
            day, month = map(int, match.groups())
            current_year = datetime.now().year
            try:
                expiry_date = datetime(current_year, month, day)
                if expiry_date < datetime.now():
                    expiry_date = datetime(current_year + 1, month, day)
                return expiry_date.strftime('%Y-%m-%d')
            except ValueError:
                print(f"Invalid date: day={day}, month={month}, year={current_year}")
                return None
    return None  # Return None for invalid dates

def process_weight(weight_str):
    if weight_str == "N/A":
        return "N/A"
    
    # Remove 'cca' and extra whitespace
    weight_str = weight_str.replace("cca", "").strip()
    
    # Convert comma to period for decimal numbers
    weight_str = weight_str.replace(",", ".")
    
    # Extract numeric value using regex
    number = re.search(r'([\d.]+)', weight_str)
    if not number:
        return "N/A"
    
    value = float(number.group(1))
    
    # Convert to kg if in grams
    if "g" in weight_str and "kg" not in weight_str:
        value = value / 1000
    
    # Return formatted string with 3 decimal places
    return f"{value:.3f}"

def main():
    try:
        print("Starting scraping process...")
        # Test if we can even launch browser
        with sync_playwright() as playwright:
            print("Playwright initialized...")
            browser = playwright.chromium.launch(headless=True)
            print("Browser launched...")
            page = browser.new_page()
            print("Page created...")
            
            # Test basic navigation
            print(f"Navigating to {PRODUCTS_URL}...")
            page.goto(PRODUCTS_URL)
            print("Navigation successful...")
            
            # Handle cookies on the products page
            cookie_response = page.query_elements(COOKIE_QUERY)
            if cookie_response.cookies_form.reject_btn is not None:
                cookie_response.cookies_form.reject_btn.click()

            # Extract product data after handling cookies
            product_response = page.query_data(PRODUCT_QUERY)
            
            # Get current date and datetime
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Process the data into a list of dictionaries
            processed_data = []
            for product in product_response["products"]:
                expiry_date = process_expiry_date(product.get("expiry_date", "N/A"), current_date)
                weight = process_weight(product.get("weight", "N/A"))
                
                if product.get("is_available") == False:
                    continue
                
                processed_data.append({
                    'date': current_date,
                    'datetime': current_datetime,
                    'name': product.get("name", "N/A"),
                    'current_price': product.get("current_price", "N/A"),
                    'original_price': product.get("original_price", "N/A"),
                    'discount': product.get("discount", "N/A"),
                    'weight': weight,
                    'price_per_kg': product.get("price_per_kg", "N/A"),
                    'expiry_date': expiry_date,
                    'is_available': product.get("is_available", "N/A")
                })

            # Convert to DataFrame
            df = pd.DataFrame(processed_data)
            
            # Database operations with error handling
            try:
                db_manager = DatabaseManager()
                db_manager.update_products(df)
                #db_manager.export_products_to_csv('products6.csv')
            except Exception as e:
                print(f"Database operation failed: {str(e)}")

    except Exception as e:
        print(f"ERROR in main(): {str(e)}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()