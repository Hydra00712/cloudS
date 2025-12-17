#!/bin/bash
set -e

# SIMPLEST POSSIBLE STARTUP: Just serve the HTML file
cd /home/site/wwwroot

echo "Starting HTTP server on port $PORT..."
python3 serve.py

