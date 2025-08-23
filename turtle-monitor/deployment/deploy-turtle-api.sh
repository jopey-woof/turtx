#!/bin/bash

# 🐢 Turtle Monitor API Deployment Script
# Comprehensive deployment script with validation and error handling

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="turtle-monitor"
BACKUP_DIR="/home/shrimp/backups"
LOG_FILE="/tmp/turtle-deploy.log"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}" | tee -a "$LOG_FILE"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
port_available() {
    ! netstat -tuln | grep -q ":$1 "
}

# Function to create backup
create_backup() {
    log_info "Creating backup of existing data..."
    
    if [ -d "$BACKUP_DIR" ]; then
        log_warning "Backup directory already exists"
    else
        mkdir -p "$BACKUP_DIR"
        log_success "Created backup directory: $BACKUP_DIR"
    fi
    
    # Backup existing turtle monitor data if it exists
    if [ -d "/home/shrimp/turtle-monitor" ]; then
        tar -czf "$BACKUP_DIR/turtle-monitor-backup-$TIMESTAMP.tar.gz" \
            -C /home/shrimp turtle-monitor 2>/dev/null || true
        log_success "Backup created: turtle-monitor-backup-$TIMESTAMP.tar.gz"
    fi
    
    # Backup existing Docker volumes if they exist
    if docker volume ls | grep -q "turtle_data"; then
        docker run --rm -v turtle_data:/data -v "$BACKUP_DIR":/backup alpine tar -czf /backup/turtle-data-backup-$TIMESTAMP.tar.gz -C /data . 2>/dev/null || true
        log_success "Docker volume backup created: turtle-data-backup-$TIMESTAMP.tar.gz"
    fi
}

# Function to validate prerequisites
validate_prerequisites() {
    log_info "Validating prerequisites..."
    
    # Check if running as shrimp user
    if [ "$USER" != "shrimp" ]; then
        log_error "This script must be run as the shrimp user"
        exit 1
    fi
    
    # Check if Docker is installed
    if ! command_exists docker; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        log_error "Docker Compose is not available. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if git is available
    if ! command_exists git; then
        log_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    # Check if required ports are available
    if ! port_available 8000; then
        log_warning "Port 8000 is already in use. The turtle-api service may not start properly."
    fi
    
    if ! port_available 1883; then
        log_warning "Port 1883 is already in use. The mosquitto service may not start properly."
    fi
    
    log_success "Prerequisites validation completed"
}

# Function to check git repository
check_git_repository() {
    log_info "Checking git repository status..."
    
    # Check if we're in a git repository or can find one
    if [ ! -d ".git" ]; then
        # Try to find the git repository in parent directories
        if [ -d "../.git" ]; then
            log_info "Found git repository in parent directory, changing to turtle-monitor directory..."
            cd ..
        elif [ -d "../../.git" ]; then
            log_info "Found git repository in grandparent directory, changing to turtle-monitor directory..."
            cd ../..
        else
            log_error "Not in a git repository. Please run this script from the turtle-monitor directory."
            exit 1
        fi
    fi
    
    # Check if there are uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        log_warning "There are uncommitted changes in the repository"
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Deployment cancelled by user"
            exit 0
        fi
    fi
    
    # Pull latest changes
    log_info "Pulling latest changes from git..."
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || log_warning "Could not pull latest changes"
    
    log_success "Git repository check completed"
}

# Function to create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    # Create data directories
    mkdir -p /home/shrimp/turtle-monitor/data
    mkdir -p /home/shrimp/turtle-monitor/logs
    
    # Set proper permissions
    chmod 755 /home/shrimp/turtle-monitor/data
    chmod 755 /home/shrimp/turtle-monitor/logs
    
    log_success "Directories created successfully"
}

# Function to build and start services
deploy_services() {
    log_info "Building and starting Docker services..."
    
    # Change to deployment directory (use absolute path to be sure)
    log_info "Current directory before cd: $(pwd)"
    cd /home/shrimp/turtx/turtle-monitor/deployment || {
        log_error "Failed to change to deployment directory"
        exit 1
    }
    log_info "Current directory after cd: $(pwd)"
    log_info "Checking if docker-compose.yml exists:"
    ls -la docker-compose.yml || log_error "docker-compose.yml not found"
    
    # Build and start services
    log_info "Building turtle-api service..."
    docker-compose -f docker-compose.yml build turtle-api
    
    log_info "Starting all services..."
    docker-compose -f docker-compose.yml up -d
    
    log_success "Services started successfully"
}

# Function to wait for services to be healthy
wait_for_services() {
    log_info "Waiting for services to be healthy..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts"
        
        # Check turtle-api health
        if curl -f http://localhost:8000/api/health >/dev/null 2>&1; then
            log_success "Turtle API is healthy"
            
            # Note: MQTT health check skipped - using existing MQTT service from /home/shrimp/turtx/docker/
            log_info "Using existing MQTT service from main docker setup"
            return 0
        else
            log_warning "Turtle API health check failed"
        fi
        
        sleep 10
        ((attempt++))
    done
    
    log_error "Services failed to become healthy within expected time"
    return 1
}

# Function to test API endpoints
test_api_endpoints() {
    log_info "Testing API endpoints..."
    
    # Test health endpoint
    if curl -f http://localhost:8000/api/health >/dev/null 2>&1; then
        log_success "Health endpoint is working"
    else
        log_error "Health endpoint test failed"
        return 1
    fi
    
    # Test latest readings endpoint
    if curl -f http://localhost:8000/api/latest >/dev/null 2>&1; then
        log_success "Latest readings endpoint is working"
    else
        log_error "Latest readings endpoint test failed"
        return 1
    fi
    
    # Test frontend
    if curl -f http://localhost:8000/ >/dev/null 2>&1; then
        log_success "Frontend is accessible"
    else
        log_error "Frontend test failed"
        return 1
    fi
    
    log_success "All API endpoint tests passed"
    return 0
}

# Function to test MQTT connectivity
test_mqtt_connectivity() {
    log_info "Testing MQTT connectivity..."
    
    # Test MQTT connection
    if docker exec turtle-monitor-mqtt mosquitto_pub -h localhost -t turtle/test -m "test_message" >/dev/null 2>&1; then
        log_success "MQTT publish test passed"
    else
        log_error "MQTT publish test failed"
        return 1
    fi
    
    # Test MQTT subscription
    if docker exec turtle-monitor-mqtt mosquitto_sub -h localhost -t turtle/test -C 1 >/dev/null 2>&1; then
        log_success "MQTT subscription test passed"
    else
        log_error "MQTT subscription test failed"
        return 1
    fi
    
    log_success "MQTT connectivity tests passed"
    return 0
}

# Function to show deployment summary
show_summary() {
    log_info "🐢 Turtle Monitor API Deployment Summary"
    echo "================================================"
    echo "✅ Services Status:"
    docker-compose -f docker-compose.yml ps
    echo ""
    echo "🌐 Access URLs:"
    echo "   Frontend: http://localhost:8000"
    echo "   API Health: http://localhost:8000/api/health"
    echo "   API Latest: http://localhost:8000/api/latest"
    echo ""
    echo "📊 MQTT Topics:"
    echo "   Shell Temperature: turtle/sensors/sensor1/temperature"
    echo "   Shell Humidity: turtle/sensors/sensor1/humidity"
    echo "   Enclosure Temperature: turtle/sensors/sensor2/temperature"
    echo "   Enclosure Humidity: turtle/sensors/sensor2/humidity"
    echo ""
    echo "📁 Data Location:"
    echo "   Database: /home/shrimp/turtle-monitor/data"
    echo "   Logs: /home/shrimp/turtle-monitor/logs"
    echo "   Backups: $BACKUP_DIR"
    echo ""
    echo "🔧 Management Commands:"
    echo "   View logs: docker-compose -f docker-compose.yml logs -f"
    echo "   Restart: docker-compose -f docker-compose.yml restart"
    echo "   Stop: docker-compose -f docker-compose.yml down"
    echo "   Update: git pull && docker-compose -f docker-compose.yml up -d --build"
    echo ""
}

# Function to handle rollback
rollback() {
    log_error "Deployment failed. Starting rollback..."
    
    # Stop services
    cd /home/shrimp/turtle-monitor/deployment
    docker-compose -f docker-compose.yml down 2>/dev/null || true
    
    # Remove created containers and images
    docker rm -f turtle-monitor-api turtle-monitor-mqtt 2>/dev/null || true
    docker rmi turtle-monitor_turtle-api 2>/dev/null || true
    
    log_warning "Rollback completed. Check the logs for more details: $LOG_FILE"
}

# Main deployment function
main() {
    log_info "Starting Turtle Monitor API deployment..."
    
    # Initialize log file
    echo "Turtle Monitor API Deployment Log - $(date)" > "$LOG_FILE"
    
    # Set up error handling
    trap rollback ERR
    
    # Run deployment steps
    validate_prerequisites
    create_backup
    check_git_repository
    create_directories
    deploy_services
    wait_for_services
    test_api_endpoints
    test_mqtt_connectivity
    
    # Remove error trap on success
    trap - ERR
    
    log_success "🎉 Turtle Monitor API deployment completed successfully!"
    show_summary
    
    log_info "Deployment log saved to: $LOG_FILE"
}

# Check if script is being sourced or run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 