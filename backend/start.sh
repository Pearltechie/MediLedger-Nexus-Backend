#!/bin/bash

# MediLedger Nexus Backend Startup Script
# This script sets up the Python path and starts the FastAPI application

# Change to the project root directory (parent of backend)
cd "$(dirname "$0")/.."

# Set the Python path to include the backend/src directory
export PYTHONPATH="$(pwd)/backend/src:${PYTHONPATH}"

# Start the FastAPI application using gunicorn with WSGI
exec gunicorn wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --worker-class uvicorn.workers.UvicornWorker
