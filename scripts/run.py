#!/usr/bin/env python3
"""
Main script runner for PollenPal API

Provides npm-like commands for development and production tasks.
Similar to package.json scripts but for Python projects.
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd, description=None):
    """Run a command and handle errors."""
    if description:
        print(f"🚀 {description}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        sys.exit(e.returncode)


def show_help():
    """Show available commands."""
    print("""
🌟 PollenPal API - Available Commands

📦 DEVELOPMENT:
  dev              Start development server with auto-reload
  dev:docker       Start development server in Docker
  install          Install dependencies with uv
  install:pip      Install dependencies with pip

🧪 TESTING:
  test             Run all tests
  test:unit        Run unit tests only
  test:integration Run integration tests only
  test:docker      Run Docker container tests
  test:watch       Run tests in watch mode
  lint             Run code quality checks
  lint:fix         Fix formatting issues

🏗️  BUILD & DEPLOY:
  build            Build production Docker image
  build:no-cache   Build without Docker cache
  deploy           Deploy to production
  deploy:dev       Deploy development environment
  start            Start production services
  stop             Stop all services
  restart          Restart services
  logs             View service logs
  status           Show service status

🔧 UTILITIES:
  clean            Clean up Docker images and containers
  shell            Open shell in running container
  db:reset         Reset database (if applicable)
  health           Check service health

📚 DOCUMENTATION:
  docs:serve       Serve API documentation locally
  docs:build       Build documentation

Use: python scripts/run.py <command>
Example: python scripts/run.py dev
""")


def main():
    parser = argparse.ArgumentParser(
        description="PollenPal API Script Runner",
        add_help=False
    )
    parser.add_argument("command", nargs="?", help="Command to run")
    parser.add_argument("args", nargs="*", help="Additional arguments")
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Change to project directory
    import os
    os.chdir(project_root)
    
    if not args.command or args.command in ["help", "-h", "--help"]:
        show_help()
        return
    
    command = args.command.lower()
    extra_args = " ".join(args.args) if args.args else ""
    
    # Development commands
    if command == "dev":
        run_command("python scripts/run_dev.py", "Starting development server")
    
    elif command == "dev:docker":
        run_command("docker-compose --profile dev up", "Starting development server in Docker")
    
    elif command == "install":
        run_command("uv sync", "Installing dependencies with uv")
        run_command("uv pip install -e .", "Installing package in development mode")
    
    elif command == "install:pip":
        run_command("pip install -e .", "Installing dependencies with pip")
    
    # Testing commands
    elif command == "test":
        run_command(f"python scripts/test.py {extra_args}", "Running all tests")
    
    elif command == "test:unit":
        run_command("python scripts/test.py --unit", "Running unit tests")
    
    elif command == "test:integration":
        run_command("python scripts/test.py --integration", "Running integration tests")
    
    elif command == "test:docker":
        run_command("python scripts/test.py --docker", "Running Docker tests")
    
    elif command == "test:watch":
        run_command("pytest tests/ --watch", "Running tests in watch mode")
    
    elif command == "lint":
        run_command("python scripts/test.py --lint", "Running code quality checks")
    
    elif command == "lint:fix":
        run_command("python scripts/test.py --fix", "Fixing code formatting")
    
    # Build and deploy commands
    elif command == "build":
        run_command(f"python scripts/build.py {extra_args}", "Building production Docker image")
    
    elif command == "build:no-cache":
        run_command("python scripts/build.py --no-cache", "Building without cache")
    
    elif command == "deploy":
        run_command(f"python scripts/deploy.py --env prod {extra_args}", "Deploying to production")
    
    elif command == "deploy:dev":
        run_command(f"python scripts/deploy.py --env dev {extra_args}", "Deploying development environment")
    
    elif command == "start":
        run_command("docker-compose --profile prod up -d", "Starting production services")
    
    elif command == "stop":
        run_command("docker-compose down", "Stopping all services")
    
    elif command == "restart":
        run_command("docker-compose down && docker-compose --profile prod up -d", "Restarting services")
    
    elif command == "logs":
        service = extra_args or ""
        run_command(f"docker-compose logs -f {service}", f"Viewing logs {service}".strip())
    
    elif command == "status":
        run_command("docker-compose ps", "Showing service status")
    
    # Utility commands
    elif command == "clean":
        print("🧹 Cleaning up Docker resources...")
        run_command("docker system prune -f", "Cleaning Docker system")
        run_command("docker image prune -f", "Cleaning Docker images")
    
    elif command == "shell":
        container = extra_args or "pollenpal-prod"
        run_command(f"docker exec -it {container} /bin/bash", f"Opening shell in {container}")
    
    elif command == "health":
        import requests
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                print("✅ Service is healthy!")
                print(f"Response: {response.json()}")
            else:
                print(f"❌ Service unhealthy (status: {response.status_code})")
        except Exception as e:
            print(f"❌ Cannot reach service: {e}")
    
    # Documentation commands
    elif command == "docs:serve":
        print("📚 API documentation available at:")
        print("   • http://localhost:3000/docs (development)")
        print("   • http://localhost:8000/docs (production)")
        print("Starting development server for docs...")
        run_command("python scripts/run_dev.py", "Starting development server")
    
    elif command == "docs:build":
        print("📖 Building documentation...")
        print("API documentation is auto-generated by FastAPI")
        print("Available at /docs and /redoc endpoints")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python scripts/run.py help' to see available commands")
        sys.exit(1)


if __name__ == "__main__":
    main() 