import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine

class DatabaseManager:
    def __init__(self):
        load_dotenv()
        self.conn_params = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT", "5432")
        }
        # Create SQLAlchemy engine
        self.engine = create_engine(f'postgresql://{self.conn_params["user"]}:{self.conn_params["password"]}@{self.conn_params["host"]}:{self.conn_params["port"]}/{self.conn_params["dbname"]}')

    def connect(self):
        return psycopg2.connect(**self.conn_params)
      
                        
    def update_products(self, df):
        """
        Replaces all records in the products table with new data
        """
        with self.connect() as conn:
            with conn.cursor() as cur:
                # Clear existing records
                cur.execute("TRUNCATE TABLE products")
                
                # Make a copy and convert all types explicitly
                df = df.copy()
                
                # Date and datetime conversions
                df['date'] = pd.to_datetime(df['date']).dt.date
                df['datetime'] = pd.to_datetime(df['datetime'])
                df['expiry_date'] = pd.to_datetime(df['expiry_date']).dt.date
                
                # Convert numeric columns - force Python float
                df['current_price'] = df['current_price'].astype(str).astype(float)
                df['original_price'] = df['original_price'].astype(str).astype(float)
                df['price_per_kg'] = df['price_per_kg'].astype(str).astype(float)
                
                # Handle discount (stored as VARCHAR in DB)
                df['discount'] = df['discount'].astype(str)
                
                # Handle weight - first ensure it's string, then extract numbers
                df['weight'] = df['weight'].astype(str)
                df['weight'] = pd.to_numeric(df['weight'].str.replace(r'[^\d.]', ''), errors='coerce')
                
                # Convert boolean - force Python bool
                df['is_available'] = df['is_available'].map(lambda x: bool(str(x).lower() == 'true'))
                
                # Convert to list of tuples with explicit Python types
                records = []
                for _, row in df.iterrows():
                    record = (
                        row['date'],
                        row['datetime'],
                        str(row['name']),
                        float(row['current_price']),
                        float(row['original_price']),
                        str(row['discount']),
                        float(row['weight']),
                        float(row['price_per_kg']),
                        row['expiry_date'],
                        bool(row['is_available'])
                    )
                    records.append(record)
                
                # Insert new records
                execute_values(cur, """
                    INSERT INTO products 
                    (date, datetime, name, current_price, original_price, 
                     discount, weight, price_per_kg, expiry_date, is_available)
                    VALUES %s
                """, records)
                
                conn.commit()

    def update_recipes(self, df):
        """
        Replaces all records in the recipes table with new data
        """
        with self.connect() as conn:
            with conn.cursor() as cur:
                # Clear existing records
                cur.execute("TRUNCATE TABLE recipes")
                
                # Make a copy and convert all types explicitly
                df = df.copy()
                
                # Convert string columns to Python str
                string_columns = ['product', 'product_english', 'recipe_name', 'instructions', 'recipe_url']
                for col in string_columns:
                    df[col] = df[col].astype(str)
                
                # Convert integer columns to Python int
                df['cooking_time'] = df['cooking_time'].astype(int)
                df['servings'] = df['servings'].astype(int)
                
                # Convert to list of tuples with explicit Python types
                records = []
                for _, row in df.iterrows():
                    record = (
                        str(row['product']),
                        str(row['product_english']),
                        str(row['recipe_name']),
                        int(row['cooking_time']),
                        int(row['servings']),
                        str(row['instructions']),
                        str(row['recipe_url']),
                        row['missing_ingredients'] if isinstance(row['missing_ingredients'], list) else None
                    )
                    records.append(record)
                
                # Insert new records
                execute_values(cur, """
                    INSERT INTO recipes 
                    (product, product_english, recipe_name, cooking_time, 
                     servings, instructions, recipe_url, missing_ingredients)
                    VALUES %s
                """, records)
                
                conn.commit()

    def get_products(self):
        """
        Retrieves all products
        """
        query = """
            SELECT * FROM products 
            ORDER BY datetime DESC
        """
        return pd.read_sql(query, self.engine)  # Use engine instead of connection

    def get_recipes(self):
        """
        Retrieves all recipes
        """
        query = "SELECT * FROM recipes"
        return pd.read_sql(query, self.engine)  # Use engine instead of connection

    def export_products_to_csv(self, filename='products_export.csv'):
        """
        Export products table to CSV with proper encoding
        """
        with self.connect() as conn:
            # Create a cursor with dictionary output
            with conn.cursor() as cur:
                # Copy to CSV with proper encoding and headers
                with open(filename, 'w', encoding='utf-8') as f:
                    # Write headers first
                    headers = ['id', 'date', 'datetime', 'name', 'current_price', 
                              'original_price', 'discount', 'weight', 'price_per_kg', 
                              'expiry_date', 'is_available']
                    f.write(','.join(headers) + '\n')
                    
                    # Copy data
                    cur.copy_expert(f"""
                        COPY (
                            SELECT id, 
                                   date, 
                                   datetime, 
                                   name, 
                                   current_price, 
                                   original_price, 
                                   discount, 
                                   weight, 
                                   price_per_kg, 
                                   expiry_date, 
                                   is_available
                            FROM products
                            ORDER BY datetime DESC
                        ) 
                        TO STDOUT 
                        WITH (FORMAT CSV, ENCODING 'utf-8')
                    """, f)
            
            print(f"Data exported to {filename}")

    def export_recipes_to_csv(self, filename='recipes_export.csv'):
        """
        Export recipes table to CSV with proper encoding
        """
        with self.connect() as conn:
            # Create a cursor with dictionary output
            with conn.cursor() as cur:
                # Copy to CSV with proper encoding and headers
                with open(filename, 'w', encoding='utf-8') as f:
                    # Write headers first
                    headers = ['id', 'product', 'product_english', 'recipe_name', 
                              'cooking_time', 'servings', 'instructions', 
                              'recipe_url', 'missing_ingredients']
                    f.write(','.join(headers) + '\n')
                    
                    # Copy data
                    cur.copy_expert(f"""
                        COPY (
                            SELECT id,
                                   product,
                                   product_english,
                                   recipe_name,
                                   cooking_time,
                                   servings,
                                   instructions,
                                   recipe_url,
                                   array_to_string(missing_ingredients, '|') as missing_ingredients
                            FROM recipes
                            ORDER BY id
                        ) 
                        TO STDOUT 
                        WITH (FORMAT CSV, ENCODING 'utf-8')
                    """, f)
            
            print(f"Data exported to {filename}")

