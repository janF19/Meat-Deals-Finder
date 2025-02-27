# Meat Deals Recipe Finder 🥩

A full-stack application that tracks discounted meat products from online grocery store Rohlik and suggests matching recipes. The system automatically scrapes product data, translates descriptions using OpenAI, and finds recipe recommendations through Spoonacular API.

## Features

- Automated scraping of discounted meat products using AGENTQL
- Recipe recommendations based on available discounted products
- Translation services powered by OpenAI API
- Interactive dashboard built with React
- RESTful API endpoints using FastAPI
- Scheduled data collection and updates
- Persistent storage using PostgreSQL

## Architecture

- **Backend**: Python (FastAPI)
- **Frontend**: React
- **Database**: PostgreSQL
- **APIs**: 
  - AGENTQL for web scraping
  - OpenAI API for translations
  - Spoonacular API for recipe recommendations

## Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL
- Required API keys:
  ```
  OPENAI_API_KEY=your_openai_key
  AGENTQL_API_KEY=your_agentql_key
  SPOONACULAR_API_KEY=your_spoonacular_key
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone [repo-url]
   cd meat-deals-recipe-finder
   ```

2. Set up the backend:
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your API keys and database configuration
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```

4. Initialize the database:
   ```bash
      # Set up database connection in .env
   DATABASE_URL=postgresql://username:password@localhost:5432/rohli_db

   # Initialize database schema
   psql -d rohli_db -f rohlikData/schema.sql
   ```

## Running the Application

1. Start the backend server:
   ```bash
   python server.py
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# API Keys
OPENAI_API_KEY=your_openai_key
AGENTQL_API_KEY=your_agentql_key
SPOONACULAR_API_KEY=your_spoonacular_key






I tried to do custom search serper call and process with beuatiful soup and llm to find czech recipe but difficult to get good results.
