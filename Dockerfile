FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    chromium \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatspi2.0-0 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    tor \
    privoxy \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    # Dependencies for Playwright
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install requirements with pip and ensure executables are in PATH
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir fastapi uvicorn

RUN pip install --no-cache-dir "uvicorn[standard]" && \
which uvicorn

RUN playwright install chromium && \
    playwright install-deps chromium

# Copy the rest of the application
COPY . .

# Add the root directory to PYTHONPATH
ENV PYTHONPATH=/app

# Expose the port
EXPOSE 8000

# Environment variables
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
    REACT_APP_API_URL='' \
    PYTHONUNBUFFERED=1

# Set display environment variable
ENV DISPLAY=:99

# Add Tor configuration
COPY torrc /etc/tor/torrc
RUN service tor start

# Add startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Run uvicorn with python -m to ensure proper module resolution
CMD ["/start.sh"]