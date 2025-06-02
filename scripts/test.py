#!/usr/bin/env python3
"""
Test runner script for PollenPal API

Runs comprehensive tests including unit tests, integration tests, and Docker container tests.
"""

import subprocess
import sys
import argparse
import time
import requests
from pathlib import Path


def run_command(cmd, description, capture_output=True, check=True):
    """Run a command and handle errors."""
    print(f"🧪 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=check, 
            capture_output=capture_output, text=True
        )
        if result.returncode == 0:
            print(f"✅ {description} passed")
            return result.stdout if capture_output else None
        else:
            print(f"❌ {description} failed")
            if capture_output and result.stderr:
                print(f"Error: {result.stderr}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        if capture_output and e.stderr:
            print(f"Error: {e.stderr}")
        return None


def wait_for_service(url, timeout=60, interval=2):
    """Wait for service to become available."""
    print(f"⏳ Waiting for service at {url}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Service is ready!")
                return True
        except requests.RequestException:
            pass
        time.sleep(interval)
    
    print(f"❌ Service not ready within {timeout}s")
    return False


def run_unit_tests():
    """Run unit tests."""
    print("\n🔬 Running Unit Tests")
    print("=" * 50)
    
    # Run pytest with coverage
    cmd = "pytest tests/ -v --cov=src/pollenpal --cov-report=term-missing --cov-report=html"
    result = run_command(cmd, "Unit tests with coverage", capture_output=False, check=False)
    return result is not None


def run_integration_tests():
    """Run integration tests."""
    print("\n🔗 Running Integration Tests")
    print("=" * 50)
    
    # Run integration tests specifically
    cmd = "pytest tests/test_integration.py -v"
    result = run_command(cmd, "Integration tests", capture_output=False, check=False)
    return result is not None


def run_docker_tests():
    """Run Docker container tests."""
    print("\n🐳 Running Docker Container Tests")
    print("=" * 50)
    
    # Build test image
    build_result = run_command(
        "docker build -t pollenpal:test --target production .",
        "Building test Docker image"
    )
    if not build_result:
        return False
    
    # Start container for testing
    run_command(
        "docker run -d --name pollenpal-test -p 8001:8000 pollenpal:test",
        "Starting test container"
    )
    
    # Wait for service
    service_ready = wait_for_service("http://localhost:8001/health")
    
    if service_ready:
        # Run API tests against container
        test_results = []
        
        # Test health endpoint
        try:
            response = requests.get("http://localhost:8001/health", timeout=10)
            if response.status_code == 200:
                print("✅ Health endpoint test passed")
                test_results.append(True)
            else:
                print("❌ Health endpoint test failed")
                test_results.append(False)
        except Exception as e:
            print(f"❌ Health endpoint test failed: {e}")
            test_results.append(False)
        
        # Test API root
        try:
            response = requests.get("http://localhost:8001/", timeout=10)
            if response.status_code == 200:
                print("✅ API root endpoint test passed")
                test_results.append(True)
            else:
                print("❌ API root endpoint test failed")
                test_results.append(False)
        except Exception as e:
            print(f"❌ API root endpoint test failed: {e}")
            test_results.append(False)
        
        # Test pollen endpoint (might fail due to external dependency)
        try:
            response = requests.get("http://localhost:8001/pollen/London", timeout=15)
            if response.status_code in [200, 404, 500]:  # Accept various responses
                print("✅ Pollen endpoint test passed (endpoint accessible)")
                test_results.append(True)
            else:
                print("❌ Pollen endpoint test failed")
                test_results.append(False)
        except Exception as e:
            print(f"⚠️  Pollen endpoint test warning: {e}")
            test_results.append(True)  # Don't fail on external dependency issues
    else:
        test_results = [False]
    
    # Cleanup
    run_command("docker stop pollenpal-test", "Stopping test container", check=False)
    run_command("docker rm pollenpal-test", "Removing test container", check=False)
    run_command("docker rmi pollenpal:test", "Removing test image", check=False)
    
    return all(test_results)


def run_linting():
    """Run code quality checks."""
    print("\n🎨 Running Code Quality Checks")
    print("=" * 50)
    
    results = []
    
    # Check if black would make changes
    black_result = run_command(
        "black --check src/ tests/",
        "Black formatting check",
        check=False
    )
    results.append(black_result is not None)
    
    # Check if isort would make changes
    isort_result = run_command(
        "isort --check-only src/ tests/",
        "Import sorting check",
        check=False
    )
    results.append(isort_result is not None)
    
    return all(results)


def main():
    parser = argparse.ArgumentParser(description="Run PollenPal API tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--docker", action="store_true", help="Run Docker tests only")
    parser.add_argument("--lint", action="store_true", help="Run linting only")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    parser.add_argument("--fix", action="store_true", help="Fix formatting issues")
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Change to project directory
    import os
    os.chdir(project_root)
    
    print("🧪 PollenPal API Test Suite")
    print("=" * 50)
    
    # Fix formatting if requested
    if args.fix:
        print("\n🔧 Fixing Code Formatting")
        print("=" * 50)
        run_command("black src/ tests/", "Formatting with Black", capture_output=False)
        run_command("isort src/ tests/", "Sorting imports with isort", capture_output=False)
        return
    
    # Determine which tests to run
    run_all = args.all or not any([args.unit, args.integration, args.docker, args.lint])
    
    results = []
    
    if args.lint or run_all:
        results.append(run_linting())
    
    if args.unit or run_all:
        results.append(run_unit_tests())
    
    if args.integration or run_all:
        results.append(run_integration_tests())
    
    if args.docker or run_all:
        results.append(run_docker_tests())
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    if all(results):
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        print("\n💡 Tips:")
        print("   • Run 'python scripts/test.py --fix' to fix formatting issues")
        print("   • Run individual test suites to isolate issues")
        print("   • Check logs for detailed error information")
        sys.exit(1)


if __name__ == "__main__":
    main() 