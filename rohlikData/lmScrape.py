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
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            
            # Create a regular Playwright page first
            playwright_page = context.new_page()
            
            # Then wrap it with AgentQL
            page = agentql.wrap(playwright_page)
            
            print(f"Navigating to {PRODUCTS_URL}...")
            page.goto(PRODUCTS_URL)
            
            # Handle cookies if they appear
            try:
                reject_button = page.locator('[data-test="CookiesDialog-decline"]')
                if reject_button.is_visible(timeout=5000):
                    reject_button.click()
                    print("Cookie banner handled")
            except Exception as e:
                print("No cookie banner found or already accepted")
            
            # Use AgentQL query
            print("Querying products...")
            product_response = page.query_elements(PRODUCT_QUERY)  # Changed from query_data to query_elements
            products_data = product_response.to_data()  # Convert response to dictionary
            products = products_data.get('products', [])
            print(f"Found {len(products)} products")
            
            # Get current date and datetime
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Process the data into a list of dictionaries
            processed_data = []
            for product in products:
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
                print("Attempting database update...")
                db_manager = DatabaseManager()
                db_manager.update_products(df)
            except Exception as e:
                print(f"Database operation failed: {str(e)}")

            # Clean up
            browser.close()

    except Exception as e:
        print(f"ERROR in main(): {str(e)}")
        print("Scraping failed")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()