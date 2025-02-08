# Backend Dockerfile
# ./Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Add missing environment variables
ENV AGENTQL_API_KEY=${AGENTQL_API_KEY} \
    SGAI_API_KEY=${SGAI_API_KEY} \
    SPOONACULAR_API_KEY=${SPOONACULAR_API_KEY} \
    OPENAI_API_KEY=${OPENAI_API_KEY} \
    DB_NAME=${DB_NAME} \
    DB_USER=${DB_USER} \
    DB_PASSWORD=${DB_PASSWORD} \
    DB_HOST=${DB_HOST} \
    DB_PORT=${DB_PORT} \
    FRONTEND_URL=${FRONTEND_URL} \
    BACKEND_URL=${BACKEND_URL} \
    ALLOWED_ORIGINS=${ALLOWED_ORIGINS} \
    REACT_APP_API_URL=${REACT_APP_API_URL} 


# Command to run the application
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]