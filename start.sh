#!/bin/bash

# MediLedger Nexus Startup Script for Render
# This script ensures the correct start command is used

echo "Starting MediLedger Nexus with gunicorn..."

# Required secrets must be configured by the deployment environment.
: "${SECRET_KEY:?SECRET_KEY must be set}"
: "${ENCRYPTION_KEY:?ENCRYPTION_KEY must be set}"
export DATABASE_URL=${DATABASE_URL:-"sqlite:///./mediledger_nexus.db"}

# Start the application with gunicorn
exec gunicorn wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --worker-class uvicorn.workers.UvicornWorker
