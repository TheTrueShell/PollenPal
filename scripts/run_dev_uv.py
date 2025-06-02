#!/usr/bin/env python3
"""
Development server runner for PollenPal API using uv

Runs the FastAPI server with auto-reload for development using the installed package.
"""

import uvicorn

if __name__ == "__main__":
    print("Starting PollenPal API development server...")
    print("API will be available at: http://localhost:3000")
    print("API documentation: http://localhost:3000/docs")
    print("Press CTRL+C to stop the server")
    
    uvicorn.run(
        "pollenpal.api.main:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        reload_dirs=["./src"],
        log_level="info",
    ) 