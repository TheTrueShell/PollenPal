#!/bin/bash

# PollenPal Docker Deployment & Management Script
# Usage: ./scripts/deploy.sh [COMMAND] [OPTIONS]

set -e

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Colour

# Default values
ENVIRONMENT="dev"
BUILD_FLAG=""
COMPOSE_FILE="docker-compose.yml"
COMMAND=""

# Function to print coloured output
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

print_header() {
    echo -e "${CYAN}=== $1 ===${NC}"
}

# Function to show usage
show_usage() {
    echo -e "${CYAN}PollenPal Docker Management Script${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [ENVIRONMENT] [OPTIONS]"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  deploy    - Deploy the application (default)"
    echo "  start     - Start existing containers"
    echo "  stop      - Stop all containers"
    echo "  restart   - Restart all containers"
    echo "  status    - Show container status"
    echo "  logs      - Show container logs"
    echo "  shell     - Open shell in API container"
    echo "  cleanup   - Remove containers and volumes"
    echo "  monitor   - Monitor container resources"
    echo "  health    - Check application health"
    echo "  backup    - Backup application data"
    echo "  update    - Update and redeploy"
    echo ""
    echo -e "${YELLOW}Environment:${NC}"
    echo "  dev       - Development environment (default)"
    echo "  prod      - Production environment with nginx"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  --build   - Build images before deploying"
    echo "  --rebuild - Rebuild images from scratch (no cache)"
    echo "  --follow  - Follow logs in real-time"
    echo "  --tail N  - Show last N lines of logs (default: 50)"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 deploy dev --build     # Build and deploy development"
    echo "  $0 logs prod --follow     # Follow production logs"
    echo "  $0 status                 # Show container status"
    echo "  $0 shell dev              # Open shell in dev API container"
    echo "  $0 cleanup prod           # Clean up production containers"
}

# Function to check prerequisites
check_prerequisites() {
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

    # Check if compose file exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        print_error "Compose file ${COMPOSE_FILE} not found!"
        exit 1
    fi
}

# Function to set environment
set_environment() {
    case $1 in
        prod|production)
            ENVIRONMENT="prod"
            COMPOSE_FILE="docker-compose.prod.yml"
            ;;
        dev|development|"")
            ENVIRONMENT="dev"
            COMPOSE_FILE="docker-compose.yml"
            ;;
        *)
            print_error "Unknown environment: $1"
            exit 1
            ;;
    esac
}

# Function to deploy application
deploy_app() {
    print_header "Deploying PollenPal API in ${ENVIRONMENT} mode"
    print_status "Using compose file: ${COMPOSE_FILE}"

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

    # Check health
    check_health
    
    show_deployment_info
}

# Function to start containers
start_containers() {
    print_header "Starting PollenPal containers"
    docker-compose -f "$COMPOSE_FILE" start
    print_success "Containers started successfully!"
    show_status
}

# Function to stop containers
stop_containers() {
    print_header "Stopping PollenPal containers"
    docker-compose -f "$COMPOSE_FILE" stop
    print_success "Containers stopped successfully!"
}

# Function to restart containers
restart_containers() {
    print_header "Restarting PollenPal containers"
    docker-compose -f "$COMPOSE_FILE" restart
    print_success "Containers restarted successfully!"
    show_status
}

# Function to show container status
show_status() {
    print_header "Container Status"
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    print_status "Docker system information:"
    docker system df
}

# Function to show logs
show_logs() {
    local tail_lines=${TAIL_LINES:-50}
    local follow_flag=""
    
    if [[ "$FOLLOW_LOGS" == "true" ]]; then
        follow_flag="-f"
        print_header "Following PollenPal logs (Ctrl+C to exit)"
    else
        print_header "PollenPal logs (last $tail_lines lines)"
    fi
    
    docker-compose -f "$COMPOSE_FILE" logs $follow_flag --tail=$tail_lines
}

# Function to open shell in API container
open_shell() {
    print_header "Opening shell in PollenPal API container"
    local container_name="pollenpal-api"
    
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "$container_name.*Up"; then
        print_status "Opening bash shell in $container_name..."
        docker-compose -f "$COMPOSE_FILE" exec pollenpal-api /bin/bash
    else
        print_error "Container $container_name is not running. Start it first with: $0 start $ENVIRONMENT"
        exit 1
    fi
}

# Function to cleanup containers and volumes
cleanup() {
    print_header "Cleaning up PollenPal containers and volumes"
    print_warning "This will remove all containers, networks, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Stopping and removing containers..."
        docker-compose -f "$COMPOSE_FILE" down -v --remove-orphans
        
        print_status "Removing unused images..."
        docker image prune -f
        
        print_status "Removing unused volumes..."
        docker volume prune -f
        
        print_success "Cleanup completed!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to monitor container resources
monitor_resources() {
    print_header "Monitoring PollenPal container resources"
    print_status "Press Ctrl+C to exit monitoring"
    echo ""
    
    # Show real-time stats
    docker stats $(docker-compose -f "$COMPOSE_FILE" ps -q)
}

# Function to check application health
check_health() {
    local api_url
    if [[ "$ENVIRONMENT" == "prod" ]]; then
        api_url="http://localhost/health"
    else
        api_url="http://localhost:3000/health"
    fi

    print_status "Checking API health at ${api_url}..."
    for i in {1..30}; do
        if curl -f -s "$api_url" > /dev/null; then
            print_success "API is healthy!"
            return 0
        fi
        if [[ $i -eq 30 ]]; then
            print_error "API health check failed after 30 attempts"
            print_status "Checking container logs..."
            docker-compose -f "$COMPOSE_FILE" logs --tail=20 pollenpal-api
            return 1
        fi
        sleep 2
    done
}

# Function to backup application data
backup_data() {
    print_header "Backing up PollenPal data"
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    
    mkdir -p "$backup_dir"
    
    print_status "Creating backup in $backup_dir..."
    
    # Backup volumes
    docker run --rm -v pollenpal_data:/data -v "$(pwd)/$backup_dir":/backup alpine tar czf /backup/data.tar.gz -C /data .
    
    # Backup configuration
    cp docker-compose*.yml "$backup_dir/" 2>/dev/null || true
    cp .env* "$backup_dir/" 2>/dev/null || true
    
    print_success "Backup created in $backup_dir"
}

# Function to update and redeploy
update_app() {
    print_header "Updating and redeploying PollenPal"
    
    print_status "Pulling latest code..."
    git pull origin main || print_warning "Git pull failed or not in a git repository"
    
    print_status "Rebuilding and redeploying..."
    BUILD_FLAG="--build --no-cache"
    deploy_app
}

# Function to show deployment information
show_deployment_info() {
    print_success "PollenPal API deployed successfully!"
    echo ""
    echo -e "${CYAN}Available endpoints:${NC}"
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
    echo -e "${CYAN}Management commands:${NC}"
    echo "  • View logs:       $0 logs $ENVIRONMENT --follow"
    echo "  • Show status:     $0 status $ENVIRONMENT"
    echo "  • Stop services:   $0 stop $ENVIRONMENT"
    echo "  • Restart:         $0 restart $ENVIRONMENT"
    echo "  • Open shell:      $0 shell $ENVIRONMENT"
    echo "  • Monitor:         $0 monitor $ENVIRONMENT"
    echo ""

    # Test API with a sample request
    print_status "Testing API with sample request..."
    local test_url
    if [[ "$ENVIRONMENT" == "prod" ]]; then
        test_url="http://localhost/pollen/London"
    else
        test_url="http://localhost:3000/pollen/London"
    fi
    
    if curl -f -s "$test_url" | head -c 100 > /dev/null; then
        print_success "Sample API request successful!"
    else
        print_warning "Sample API request failed, but health check passed. API might still be initialising."
    fi
}

# Parse arguments
FOLLOW_LOGS="false"
TAIL_LINES=50

while [[ $# -gt 0 ]]; do
    case $1 in
        deploy|start|stop|restart|status|logs|shell|cleanup|monitor|health|backup|update)
            COMMAND="$1"
            shift
            ;;
        dev|development|prod|production)
            set_environment "$1"
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
        --follow)
            FOLLOW_LOGS="true"
            shift
            ;;
        --tail)
            TAIL_LINES="$2"
            shift 2
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

# Set default command if none provided
if [[ -z "$COMMAND" ]]; then
    COMMAND="deploy"
fi

# Set default environment
set_environment "$ENVIRONMENT"

# Check prerequisites
check_prerequisites

# Execute command
case $COMMAND in
    deploy)
        deploy_app
        ;;
    start)
        start_containers
        ;;
    stop)
        stop_containers
        ;;
    restart)
        restart_containers
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    shell)
        open_shell
        ;;
    cleanup)
        cleanup
        ;;
    monitor)
        monitor_resources
        ;;
    health)
        check_health
        ;;
    backup)
        backup_data
        ;;
    update)
        update_app
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac 