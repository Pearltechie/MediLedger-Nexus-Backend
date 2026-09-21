#!/usr/bin/env python3
"""
WSGI entry point for MediLedger Nexus Backend
This file is used by deployment platforms like Render
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

# Import the FastAPI app
from mediledger_nexus.main import app

# Export the app for WSGI servers
application = app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
