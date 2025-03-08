# Meat Deals Recipe Finder 🥩

A full-stack application that monitors discounted meat products from Rohlik (Czech online grocery store) and generates matching recipes using AI. The system automatically scrapes product data every 12 hours and suggests recipes based on the available discounted items.

## Screenshots

### Product Overview
![Product Overview](docs/image.png)

### Recipe Details
![Recipe Details](docs/image2.png)

## Features

- Automated scraping of discounted meat products from Rohlik
- AI-powered recipe generation using OpenAI API
- Translation services powered by OpenAI API
- Interactive dashboard built with React
- RESTful API endpoints using FastAPI
- Scheduled data collection and updates (every 12 hours)
- Persistent storage using PostgreSQL
- Containerized deployment using Docker Compose
- Automated CI/CD pipeline for AWS EC2 deployment

## Architecture

- **Backend**: Python (FastAPI)
- **Frontend**: React
- **Database**: PostgreSQL
- **APIs**: 
  - OpenAI API for recipe generation and translations
- **Deployment**: 
  - Docker Compose for local development
  - GitHub Actions CI/CD pipeline for AWS EC2 deployment

## Prerequisites

- Docker and Docker Compose
- Required API keys:
  ```
  OPENAI_API_KEY=your_openai_key
  ```

## Deployment Options

### Local Development with Docker Compose

1. Clone the repository:
   ```bash
   git clone [repo-url]
   cd meat-deals-recipe-finder
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and database configuration
   ```

3. Start the application:
   ```bash
   docker compose up
   ```

### AWS EC2 Deployment

The application includes a comprehensive GitHub Actions workflow for automated deployment to AWS EC2. The workflow:

- Builds and pushes Docker images to Amazon ECR
- Performs network diagnostics and SSH connectivity checks
- Deploys the application using Docker Compose
- Sets up environment variables securely
- Includes error handling and logging

Required GitHub Secrets for AWS deployment:
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
EC2_HOST
EC2_SSH_KEY
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
OPENAI_API_KEY
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


