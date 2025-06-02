#!/usr/bin/env python3
"""
Production build script for PollenPal API

Builds optimised Docker images for production deployment.
"""

import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔨 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        sys.exit(1)


def get_version():
    """Get version from pyproject.toml."""
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def main():
    parser = argparse.ArgumentParser(description="Build PollenPal Docker images")
    parser.add_argument("--tag", help="Custom tag for the image")
    parser.add_argument("--push", action="store_true", help="Push image to registry")
    parser.add_argument("--registry", default="", help="Docker registry URL")
    parser.add_argument("--platform", default="linux/amd64,linux/arm64", 
                       help="Target platforms for multi-arch build")
    parser.add_argument("--no-cache", action="store_true", help="Build without cache")
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Change to project directory
    import os
    os.chdir(project_root)
    
    # Get version and create tags
    version = get_version()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    base_name = "pollenpal"
    if args.registry:
        base_name = f"{args.registry.rstrip('/')}/{base_name}"
    
    tags = [
        f"{base_name}:latest",
        f"{base_name}:v{version}",
        f"{base_name}:v{version}-{timestamp}"
    ]
    
    if args.tag:
        tags.append(f"{base_name}:{args.tag}")
    
    print(f"🏗️  Building PollenPal API v{version}")
    print(f"📦 Tags: {', '.join(tags)}")
    
    # Build command
    cache_flag = "--no-cache" if args.no_cache else ""
    tag_flags = " ".join([f"-t {tag}" for tag in tags])
    
    build_cmd = f"""
    docker build {cache_flag} \
        --target production \
        --platform {args.platform} \
        {tag_flags} \
        --label "version={version}" \
        --label "build-date={datetime.now().isoformat()}" \
        --label "vcs-ref=$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
        .
    """.strip()
    
    run_command(build_cmd, "Building Docker image")
    
    # Push if requested
    if args.push:
        for tag in tags:
            run_command(f"docker push {tag}", f"Pushing {tag}")
    
    print(f"🎉 Build completed successfully!")
    print(f"📋 Available tags:")
    for tag in tags:
        print(f"   • {tag}")
    
    if not args.push:
        print(f"\n💡 To push images, run: python scripts/build.py --push")


if __name__ == "__main__":
    main() 