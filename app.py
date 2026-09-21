#!/usr/bin/env python3
"""
Main application entry point for MediLedger Nexus Backend
This file is used by Render for automatic deployment detection
"""

import os
import sys

# Add the backend/src directory to Python path
backend_src_path = os.path.join(os.path.dirname(__file__), 'backend', 'src')
if backend_src_path not in sys.path:
    sys.path.insert(0, backend_src_path)

# Also add the backend directory for package imports
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    # Import the FastAPI app
    from mediledger_nexus.main import app
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Backend src path: {backend_src_path}")
    print(f"Backend path exists: {os.path.exists(backend_path)}")
    print(f"Backend src path exists: {os.path.exists(backend_src_path)}")
    
    # List contents of backend directory
    if os.path.exists(backend_path):
        print(f"Backend directory contents: {os.listdir(backend_path)}")
    if os.path.exists(backend_src_path):
        print(f"Backend src directory contents: {os.listdir(backend_src_path)}")
    
    raise

# Export the app for deployment platforms
application = app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
