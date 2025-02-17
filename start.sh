#!/bin/bash
# Start Tor service
service tor start
sleep 5

# Start the application
exec uvicorn api.main:app --host 0.0.0.0 --port 8000