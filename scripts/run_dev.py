#!/usr/bin/env python3
"""
Development server runner for PollenPal API

Runs the FastAPI server with auto-reload for development.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.pollenpal.api.main:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        reload_dirs=["./src"],
        log_level="info",
    ) 