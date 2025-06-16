"""
Local FastAPI server script to run the AWS Backend API / Dashboard module for demo purposes.

Usage:
    python run_api_server.py

This script runs the FastAPI app defined in backend_api/api.py locally on http://localhost:8000
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend_api.api:app", host="0.0.0.0",
                port=8000, log_level="info")
