#!/bin/bash

# PollenPal Docker Deployment Script
# Usage: ./scripts/deploy.sh [dev|prod] [--build|--rebuild]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="dev"
BUILD_FLAG=""
COMPOSE_FILE="docker-compose.yml"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [dev|prod] [--build|--rebuild]"
    echo ""
    echo "Options:"
    echo "  dev     - Deploy development environment (default)"
    echo "  prod    - Deploy production environment with nginx"
    echo "  --build - Build images before deploying"
    echo "  --rebuild - Rebuild images from scratch (no cache)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Deploy dev environment"
    echo "  $0 prod --build       # Build and deploy production"
    echo "  $0 dev --rebuild      # Rebuild dev from scratch"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        dev|development)
            ENVIRONMENT="dev"
            COMPOSE_FILE="docker-compose.yml"
            shift
            ;;
        prod|production)
            ENVIRONMENT="prod"
            COMPOSE_FILE="docker-compose.prod.yml"
            shift
            ;;
        --build)
            BUILD_FLAG="--build"
            shift
            ;;
        --rebuild)
            BUILD_FLAG="--build --no-cache"
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install it and try again."
    exit 1
fi

print_status "Deploying PollenPal API in ${ENVIRONMENT} mode..."
print_status "Using compose file: ${COMPOSE_FILE}"

# Check if compose file exists
if [[ ! -f "$COMPOSE_FILE" ]]; then
    print_error "Compose file ${COMPOSE_FILE} not found!"
    exit 1
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f "$COMPOSE_FILE" down

# Build and start services
if [[ -n "$BUILD_FLAG" ]]; then
    print_status "Building images..."
    docker-compose -f "$COMPOSE_FILE" up -d $BUILD_FLAG
else
    print_status "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d
fi

# Wait for services to be healthy
print_status "Waiting for services to start..."
sleep 10

# Check if API is responding
if [[ "$ENVIRONMENT" == "prod" ]]; then
    API_URL="http://localhost/health"
else
    API_URL="http://localhost:3000/health"
fi

print_status "Checking API health at ${API_URL}..."
for i in {1..30}; do
    if curl -f -s "$API_URL" > /dev/null; then
        print_success "API is healthy!"
        break
    fi
    if [[ $i -eq 30 ]]; then
        print_error "API health check failed after 30 attempts"
        print_status "Checking container logs..."
        docker-compose -f "$COMPOSE_FILE" logs --tail=20 pollenpal-api
        exit 1
    fi
    sleep 2
done

# Show running containers
print_status "Running containers:"
docker-compose -f "$COMPOSE_FILE" ps

# Show useful URLs
print_success "PollenPal API deployed successfully!"
echo ""
echo "Available endpoints:"
if [[ "$ENVIRONMENT" == "prod" ]]; then
    echo "  • API Root:        http://localhost/"
    echo "  • Documentation:   http://localhost/docs"
    echo "  • Health Check:    http://localhost/health"
    echo "  • Example:         http://localhost/pollen/London"
else
    echo "  • API Root:        http://localhost:3000/"
    echo "  • Documentation:   http://localhost:3000/docs"
    echo "  • Health Check:    http://localhost:3000/health"
    echo "  • Example:         http://localhost:3000/pollen/London"
fi
echo ""
echo "Useful commands:"
echo "  • View logs:       docker-compose -f ${COMPOSE_FILE} logs -f"
echo "  • Stop services:   docker-compose -f ${COMPOSE_FILE} down"
echo "  • Restart:         docker-compose -f ${COMPOSE_FILE} restart"
echo ""

# Test API with a sample request
print_status "Testing API with sample request..."
if curl -f -s "${API_URL%/health}/pollen/London" | head -c 100 > /dev/null; then
    print_success "Sample API request successful!"
else
    print_warning "Sample API request failed, but health check passed. API might still be initialising."
fi 