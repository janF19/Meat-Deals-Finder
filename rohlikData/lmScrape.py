import os
import agentql
from playwright.sync_api import sync_playwright
import dotenv
from datetime import datetime, timedelta
import re
import sys
import pandas as pd 
import logging
import time
import traceback

# Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)



# Set up more verbose logging
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper_debug.log')  # Also save logs to a file
    ]
)
logger = logging.getLogger(__name__)

# Add these after your basic logging configuration
logging.getLogger('playwright').setLevel(logging.DEBUG)
logging.getLogger('agentql').setLevel(logging.DEBUG)

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from db_operations import DatabaseManager

dotenv.load_dotenv()

PRODUCTS_URL = "https://www.rohlik.cz/zachran-a-usetri/c300103000-maso-a-ryby/"

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
    """Process expiry date with better error handling"""
    try:
        if expiry_date_str == "Spotřebujte zítra":
            next_day = datetime.strptime(current_date, '%Y-%m-%d') + timedelta(days=1)
            return next_day.strftime('%Y-%m-%d')
        elif expiry_date_str == "dnes":
            return current_date
        
        # Try to extract date whether it has "Spotřeba do" prefix or not
        match = re.search(r'(?:Spotřeba do\s*)?(\d+)\.\s*(\d+)\.', expiry_date_str)
        if match:
            day, month = map(int, match.groups())
            current_year = datetime.now().year
            try:
                # Create date object
                expiry_date = datetime(current_year, month, day)
                
                # If the date is in the past, assume it's next year
                if expiry_date < datetime.now():
                    expiry_date = datetime(current_year + 1, month, day)
                
                logger.info(f"Processed expiry date '{expiry_date_str}' to {expiry_date.strftime('%Y-%m-%d')}")
                return expiry_date.strftime('%Y-%m-%d')
            except ValueError as ve:
                logger.warning(f"Invalid date values: day={day}, month={month}, year={current_year}: {ve}")
                return None
        else:
            logger.warning(f"Could not parse date from string: {expiry_date_str}")
            return None
    except Exception as e:
        logger.error(f"Error processing expiry date '{expiry_date_str}': {str(e)}")
        return None

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
        logger.info("Starting scraping...")
        with sync_playwright() as playwright:
            # Modified browser launch options for Docker
            browser = playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            
            page = agentql.wrap(browser.new_page())
            
            # Add page error handling
            page.on("console", lambda msg: logger.debug(f"Browser console: {msg.text}"))
            page.on("pageerror", lambda err: logger.error(f"Page error: {err}"))

            # Add timeout and retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"Navigation attempt {attempt + 1} to {PRODUCTS_URL}")
                    page.goto(PRODUCTS_URL, timeout=30000)  # 30 second timeout
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Navigation failed: {str(e)}. Retrying...")
                    time.sleep(5)

            # Extract product data
            logger.info("Querying products...")
            product_response = page.query_data(PRODUCT_QUERY)
            
            if not product_response or "products" not in product_response:
                logger.error("No products found in response")
                return
                
            logger.info(f"Found {len(product_response['products'])} products")
            
            # Process data
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            processed_data = []
            for i, product in enumerate(product_response["products"], 1):
                if product.get("is_available") == False:
                    continue
                    
                product_data = {
                    'date': current_date,
                    'datetime': current_datetime,
                    'name': product.get("name", "N/A"),
                    'current_price': product.get("current_price", "N/A"),
                    'original_price': product.get("original_price", "N/A"),
                    'discount': product.get("discount", "N/A"),
                    'weight': process_weight(product.get("weight", "N/A")),
                    'price_per_kg': product.get("price_per_kg", "N/A"),
                    'expiry_date': process_expiry_date(product.get("expiry_date", "N/A"), current_date),
                    'is_available': True
                }
                
                # Print each product as it's processed
                logger.info(f"\nProduct {i}:")
                logger.info(f"Name: {product_data['name']}")
                logger.info(f"Current Price: {product_data['current_price']}")
                logger.info(f"Original Price: {product_data['original_price']}")
                logger.info(f"Discount: {product_data['discount']}")
                logger.info(f"Weight: {product_data['weight']}")
                logger.info(f"Price per kg: {product_data['price_per_kg']}")
                logger.info(f"Expiry Date: {product_data['expiry_date']}")
                logger.info("------------------------")
                
                processed_data.append(product_data)

            # Convert to DataFrame and update database
            if processed_data:
                logger.info(f"Updating database with {len(processed_data)} products")
                df = pd.DataFrame(processed_data)
                db_manager = DatabaseManager()
                db_manager.update_products(df)
                logger.info("Database update completed")
            else:
                logger.warning("No products to update")

    except Exception as e:
        logger.error(f"Critical error in scraping: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    main()