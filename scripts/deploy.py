#!/usr/bin/env python3
"""
Production deployment script for PollenPal API

Manages production deployments using Docker Compose with health checks and rollback capabilities.
"""

import subprocess
import sys
import argparse
import time
import requests
from pathlib import Path


def run_command(cmd, description, capture_output=True):
    """Run a command and handle errors."""
    print(f"🚀 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, 
            capture_output=capture_output, text=True
        )
        if capture_output:
            print(f"✅ {description} completed successfully")
            return result.stdout
        else:
            print(f"✅ {description} completed successfully")
            return None
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        if capture_output and e.stderr:
            print(f"Error: {e.stderr}")
        sys.exit(1)


def wait_for_health_check(url, timeout=120, interval=5):
    """Wait for service to become healthy."""
    print(f"🏥 Waiting for service health check at {url}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Service is healthy!")
                return True
        except requests.RequestException:
            pass
        
        print(f"⏳ Waiting for service... ({int(time.time() - start_time)}s)")
        time.sleep(interval)
    
    print(f"❌ Service failed to become healthy within {timeout}s")
    return False


def main():
    parser = argparse.ArgumentParser(description="Deploy PollenPal API")
    parser.add_argument("--env", choices=["dev", "prod"], default="prod",
                       help="Deployment environment")
    parser.add_argument("--build", action="store_true", 
                       help="Build images before deployment")
    parser.add_argument("--no-cache", action="store_true", 
                       help="Build without cache")
    parser.add_argument("--rollback", action="store_true",
                       help="Rollback to previous deployment")
    parser.add_argument("--scale", type=int, default=1,
                       help="Number of API instances to run")
    parser.add_argument("--health-check-url", 
                       default="http://localhost:8000/health",
                       help="Health check URL")
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Change to project directory
    import os
    os.chdir(project_root)
    
    print(f"🌟 Deploying PollenPal API ({args.env} environment)")
    
    if args.rollback:
        print("🔄 Rolling back deployment...")
        run_command(
            f"docker-compose --profile {args.env} down",
            "Stopping current deployment"
        )
        # In a real scenario, you'd restore from backup or previous image
        print("⚠️  Rollback functionality requires implementation of backup/restore logic")
        return
    
    # Build if requested
    if args.build:
        build_flags = "--no-cache" if args.no_cache else ""
        run_command(
            f"python scripts/build.py {build_flags}",
            "Building Docker images"
        )
    
    # Stop existing services
    run_command(
        f"docker-compose --profile {args.env} down",
        "Stopping existing services"
    )
    
    # Start services
    compose_cmd = f"docker-compose --profile {args.env} up -d"
    if args.scale > 1 and args.env == "prod":
        compose_cmd += f" --scale pollenpal-prod={args.scale}"
    
    run_command(compose_cmd, f"Starting {args.env} services")
    
    # Wait for services to be ready
    time.sleep(10)
    
    # Health check
    if args.env == "prod":
        health_url = args.health_check_url
        if not wait_for_health_check(health_url):
            print("❌ Deployment failed - service not healthy")
            print("🔄 Rolling back...")
            run_command(
                f"docker-compose --profile {args.env} down",
                "Rolling back failed deployment"
            )
            sys.exit(1)
    
    # Show status
    run_command(
        f"docker-compose --profile {args.env} ps",
        "Showing service status",
        capture_output=False
    )
    
    print(f"🎉 Deployment completed successfully!")
    
    if args.env == "dev":
        print(f"🌐 Development API: http://localhost:3000")
        print(f"📚 API Documentation: http://localhost:3000/docs")
    else:
        print(f"🌐 Production API: http://localhost:8000")
        print(f"📚 API Documentation: http://localhost:8000/docs")
        print(f"🔒 Nginx Proxy: http://localhost:80")
    
    print(f"\n📋 Useful commands:")
    print(f"   • View logs: docker-compose --profile {args.env} logs -f")
    print(f"   • Stop services: docker-compose --profile {args.env} down")
    print(f"   • Restart: python scripts/deploy.py --env {args.env}")


if __name__ == "__main__":
    main() 