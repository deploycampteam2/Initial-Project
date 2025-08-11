#!/bin/bash

# ExploreIndonesia - Production Deployment Script
# Usage: ./deploy.sh [start|stop|restart|logs|status]

set -e

# Configuration
PROJECT_NAME="exploreindo"
COMPOSE_FILE="docker-compose.prod.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker service."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Check if model file exists
check_model() {
    if [ ! -f "./model/recommendation_artifacts_optimal.pkl" ]; then
        log_error "ML model file not found at ./model/recommendation_artifacts_optimal.pkl"
        log_info "Please ensure the model file is in the correct location."
        exit 1
    fi
}

# Start services
start_services() {
    log_info "Starting ExploreIndonesia services..."
    
    check_docker
    check_model
    
    # Build and start containers
    docker-compose -f $COMPOSE_FILE up --build -d
    
    log_success "Services started successfully!"
    log_info "Website: http://localhost (port 80)"
    log_info "API: http://localhost/api/"
    log_info "Direct Streamlit: http://localhost:8501"
    log_info "Direct API: http://localhost:8000"
    
    # Wait a bit and check health
    sleep 10
    check_health
}

# Stop services
stop_services() {
    log_info "Stopping ExploreIndonesia services..."
    docker-compose -f $COMPOSE_FILE down
    log_success "Services stopped successfully!"
}

# Restart services
restart_services() {
    log_info "Restarting ExploreIndonesia services..."
    stop_services
    sleep 5
    start_services
}

# Show logs
show_logs() {
    log_info "Showing service logs..."
    docker-compose -f $COMPOSE_FILE logs -f --tail=100
}

# Check service health
check_health() {
    log_info "Checking service health..."
    
    # Check API health
    if curl -f -s http://localhost:8000/ > /dev/null; then
        log_success "API service is healthy"
    else
        log_warning "API service might be unhealthy"
    fi
    
    # Check Streamlit health
    if curl -f -s http://localhost:8501/ > /dev/null; then
        log_success "Website service is healthy"
    else
        log_warning "Website service might be unhealthy"
    fi
    
    # Check Nginx health
    if curl -f -s http://localhost/health > /dev/null; then
        log_success "Nginx service is healthy"
    else
        log_warning "Nginx service might be unhealthy"
    fi
}

# Show service status
show_status() {
    log_info "Service Status:"
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    log_info "System Resources:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Clean up (remove containers, images, and volumes)
cleanup() {
    log_warning "This will remove all containers, images, and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "Cleaning up..."
        docker-compose -f $COMPOSE_FILE down -v --rmi all
        docker system prune -f
        log_success "Cleanup completed!"
    else
        log_info "Cleanup cancelled."
    fi
}

# Update services (pull latest code and rebuild)
update_services() {
    log_info "Updating services..."
    
    # Pull latest changes (if using git)
    if [ -d ".git" ]; then
        log_info "Pulling latest changes from git..."
        git pull
    fi
    
    # Rebuild and restart
    docker-compose -f $COMPOSE_FILE build --no-cache
    restart_services
    
    log_success "Services updated successfully!"
}

# Show help
show_help() {
    echo "ExploreIndonesia - Production Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start      Start all services"
    echo "  stop       Stop all services"
    echo "  restart    Restart all services"
    echo "  logs       Show service logs"
    echo "  status     Show service status"
    echo "  health     Check service health"
    echo "  update     Update and rebuild services"
    echo "  cleanup    Remove all containers and images"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start the application"
    echo "  $0 logs     # View logs"
    echo "  $0 status   # Check status"
}

# Main script
case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    health)
        check_health
        ;;
    update)
        update_services
        ;;
    cleanup)
        cleanup
        ;;
    help|*)
        show_help
        ;;
esac