import os
import agentql
from playwright.sync_api import sync_playwright
import dotenv
from datetime import datetime, timedelta
import re
import sys
import pandas as pd 
import traceback
import logging
import requests

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
    """Process expiry date with better error handling"""
    try:
        if expiry_date_str == "Spotřebujte zítra":
            next_day = datetime.strptime(current_date, '%Y-%m-%d') + timedelta(days=1)
            return next_day.strftime('%Y-%m-%d')
        elif "Spotřeba do" in expiry_date_str:
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
                    logger.warning(f"Invalid date values: day={day}, month={month}, year={current_year}")
                    return None
    except Exception as e:
        logger.warning(f"Error processing expiry date '{expiry_date_str}': {str(e)}")
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


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Verify AgentQL configuration
logger.info(f"AgentQL API Key set: {'AGENTQL_API_KEY' in os.environ}")
# Update this line - AgentQL now uses environment variable directly
os.environ['AGENTQL_API_KEY'] = os.environ.get('AGENTQL_API_KEY', '')

def main():
    try:
        logger.info("Starting scraping process...")
        with sync_playwright() as playwright:
            # Launch browser with additional arguments
            browser = playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-features=VizDisplayCompositor',
                ]
            )
            
            # More realistic browser context
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                locale='cs-CZ',
                timezone_id='Europe/Prague',
                extra_http_headers={
                    'Accept-Language': 'cs-CZ,cs;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
            
            playwright_page = context.new_page()
            page = agentql.wrap(playwright_page)
            
            logger.info(f"Navigating to {PRODUCTS_URL}...")
            try:
                # First visit the main page to get cookies
                logger.info("Visiting main page first...")
                main_response = page.goto(
                    "https://www.rohlik.cz",
                    timeout=60000,
                    wait_until='networkidle'
                )
                logger.info(f"Main page loaded with status: {main_response.status if main_response else 'unknown'}")
                page.wait_for_timeout(5000)
                
                # Now visit the products page
                response = page.goto(
                    PRODUCTS_URL,
                    timeout=60000,
                    wait_until='networkidle'
                )
                logger.info(f"Products page loaded with status: {response.status if response else 'unknown'}")
                
                # Add longer delay after page load
                page.wait_for_timeout(10000)
                
                # Take debug screenshot
                page.screenshot(path="/tmp/debug_page.png")
                
                # Verify page content
                page_content = page.content()
                logger.info(f"Page content length: {len(page_content)}")
                
                if "Přístup zamítnut" in page_content or "Access denied" in page_content:
                    logger.error("Access denied by Rohlik - detected by page content")
                    return
                
                if len(page_content) < 1000:
                    logger.error("Page content seems too short, possible blocking")
                    return
                
            except Exception as e:
                logger.error(f"Error loading page: {str(e)}")
                logger.error(f"Current URL: {page.url}")
                return
            
            try:
                reject_button = page.locator('[data-test="CookiesDialog-decline"]')
                if reject_button.is_visible(timeout=5000):
                    reject_button.click()
                    logger.info("Cookie banner handled")
                    page.wait_for_timeout(2000)
            except Exception as e:
                logger.warning(f"Cookie handling error: {str(e)}")
            
            logger.info("Querying products...")
            try:
                product_response = page.query_elements(PRODUCT_QUERY)
                products_data = product_response.to_data()
                products = products_data.get('products', [])
                logger.info(f"Found {len(products)} products")
                
                if len(products) == 0:
                    logger.error("No products found in response")
                    logger.debug(f"Response data: {products_data}")
                    page.screenshot(path="debug_screenshot.png")
                    return
                
            except Exception as e:
                logger.error(f"Error querying products: {str(e)}")
                return

            # Process the data into a list of dictionaries
            processed_data = []
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            for product in products:
                try:
                    # Process expiry date with fallback
                    expiry_date = process_expiry_date(product.get("expiry_date", "N/A"), current_date)
                    if expiry_date is None:
                        # Set a default expiry date (e.g., 7 days from now) if processing fails
                        default_expiry = datetime.now() + timedelta(days=7)
                        expiry_date = default_expiry.strftime('%Y-%m-%d')
                        logger.warning(f"Using default expiry date for product {product.get('name', 'Unknown')}")

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
                        'expiry_date': expiry_date,  # Now always has a valid date
                        'is_available': product.get("is_available", True)  # Default to True if not specified
                    })
                except Exception as e:
                    logger.error(f"Error processing product: {str(e)}")
                    logger.error(f"Product data: {product}")
                    continue

            # Convert to DataFrame with explicit data types
            if processed_data:
                try:
                    df = pd.DataFrame(processed_data)
                    
                    # Ensure date columns are properly formatted
                    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
                    df['datetime'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    df['expiry_date'] = pd.to_datetime(df['expiry_date']).dt.strftime('%Y-%m-%d')
                    
                    # Replace any NaT values with default dates
                    df['date'].fillna(current_date, inplace=True)
                    df['datetime'].fillna(current_datetime, inplace=True)
                    df['expiry_date'].fillna(
                        (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'), 
                        inplace=True
                    )
                    
                    logger.info(f"Attempting database update with {len(processed_data)} products...")
                    logger.debug(f"DataFrame columns: {df.columns.tolist()}")
                    db_manager = DatabaseManager()
                    db_manager.update_products(df)
                    logger.info("Database update completed successfully")
                except Exception as e:
                    logger.error(f"Database operation failed: {str(e)}", exc_info=True)
            else:
                logger.warning("No processed data available for database update")

    except Exception as e:
        logger.error(f"ERROR in main(): {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()