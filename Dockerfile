FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
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

# Environment variables declaration
ENV AGENTQL_API_KEY='' \
    SGAI_API_KEY='' \
    SPOONACULAR_API_KEY='' \
    OPENAI_API_KEY='' \
    DB_NAME='' \
    DB_USER='' \
    DB_PASSWORD='' \
    DB_HOST='' \
    DB_PORT='' \
    FRONTEND_URL='' \
    BACKEND_URL='' \
    ALLOWED_ORIGINS='' \
    REACT_APP_API_URL=''

# Change to use python to run server.py directly
CMD ["python", "server.py"]