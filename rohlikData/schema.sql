-- Products table to store product data with timestamp
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    date DATE DEFAULT CURRENT_DATE,
    datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name VARCHAR(255) NOT NULL,
    current_price DECIMAL(10,2),
    original_price DECIMAL(10,2),
    discount VARCHAR(10),
    weight DECIMAL(10,3),
    price_per_kg DECIMAL(10,2),
    expiry_date DATE,
    is_available BOOLEAN
);

-- Recipes table to store recipe recommendations
CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    product VARCHAR(255) NOT NULL,
    product_english VARCHAR(255),
    recipe_name VARCHAR(255) NOT NULL,
    cooking_time INTEGER,
    servings INTEGER,
    instructions TEXT,
    recipe_url VARCHAR(512),
    missing_ingredients TEXT[]
);

