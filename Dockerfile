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
    libnss3-dev \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create Tor configuration
RUN echo "SocksPort 9050" > /etc/tor/torrc

# Create startup script
RUN echo '#!/bin/bash\n\
Xvfb :99 -screen 0 1024x768x16 & \
service tor start\n\
sleep 5\n\
exec uvicorn api.main:app --host 0.0.0.0 --port 8000' > /start.sh && \
    chmod +x /start.sh

# Install xvfb
RUN apt-get update && apt-get install -y xvfb && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python dependencies and Playwright
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir fastapi uvicorn && \
    playwright install --with-deps chromium && \
    playwright install && \
    playwright install-deps

# Make sure the Playwright browser is installed in the correct location
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN pip install --no-cache-dir "uvicorn[standard]" && \
    which uvicorn

# Copy the application code
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
    PYTHONUNBUFFERED=1 \
    DISPLAY=:99

CMD ["/start.sh"]