#!/usr/bin/env python3
"""
Development server runner for PollenPal API

Runs the FastAPI server with auto-reload for development.
"""

import sys
import subprocess
import uvicorn
from pathlib import Path


def ensure_package_installed():
    """Ensure the package is installed in development mode."""
    try:
        # Try to import the package
        import pollenpal
        print("✓ Package already installed")
    except ImportError:
        print("Installing package in development mode...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], 
                         check=True, cwd=Path(__file__).parent.parent)
            print("✓ Package installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install package: {e}")
            sys.exit(1)


if __name__ == "__main__":
    # Ensure package is installed
    ensure_package_installed()
    
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