#!/bin/bash

# 🐢 Turtle Monitor API Test Script
# Tests the API endpoints and MQTT connectivity

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="http://localhost:8000"
MQTT_HOST="localhost"
MQTT_PORT="1883"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to test API endpoint
test_api_endpoint() {
    local endpoint="$1"
    local description="$2"
    
    log_info "Testing $description..."
    
    if command_exists curl; then
        response=$(curl -s -w "%{http_code}" "$API_URL$endpoint" 2>/dev/null || echo "000")
        http_code="${response: -3}"
        body="${response%???}"
        
        if [ "$http_code" = "200" ]; then
            log_success "$description - HTTP $http_code"
            echo "Response: $body" | head -c 200
            echo "..."
        else
            log_error "$description - HTTP $http_code"
            echo "Response: $body"
        fi
    else
        log_warning "curl not available, skipping $description"
    fi
}

# Function to test MQTT connectivity
test_mqtt() {
    log_info "Testing MQTT connectivity..."
    
    if command_exists mosquitto_pub; then
        # Test publishing a message
        if mosquitto_pub -h "$MQTT_HOST" -p "$MQTT_PORT" -t "test/turtle" -m "test" 2>/dev/null; then
            log_success "MQTT publish test successful"
        else
            log_error "MQTT publish test failed"
        fi
        
        # Test subscribing (timeout after 5 seconds)
        timeout 5 mosquitto_sub -h "$MQTT_HOST" -p "$MQTT_PORT" -t "test/turtle" -C 1 >/dev/null 2>&1 && log_success "MQTT subscribe test successful" || log_warning "MQTT subscribe test timeout (expected)"
    else
        log_warning "mosquitto_pub not available, skipping MQTT tests"
    fi
}

# Function to test Docker containers
test_containers() {
    log_info "Testing Docker containers..."
    
    if command_exists docker; then
        # Check if containers are running
        if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "turtle-monitor-api"; then
            log_success "turtle-monitor-api container is running"
        else
            log_error "turtle-monitor-api container is not running"
        fi
        
        if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "turtle-monitor-mqtt"; then
            log_success "turtle-monitor-mqtt container is running"
        else
            log_error "turtle-monitor-mqtt container is not running"
        fi
        
        # Check container logs for errors
        log_info "Checking container logs for errors..."
        if docker logs turtle-monitor-api 2>&1 | grep -i error | tail -5; then
            log_warning "Found errors in API container logs"
        else
            log_success "No errors found in API container logs"
        fi
    else
        log_warning "Docker not available, skipping container tests"
    fi
}

# Function to test sensor data flow
test_sensor_data() {
    log_info "Testing sensor data flow..."
    
    # Publish test sensor data
    if command_exists mosquitto_pub; then
        log_info "Publishing test sensor data..."
        
        # Test shell sensor data
        mosquitto_pub -h "$MQTT_HOST" -p "$MQTT_PORT" -t "turtle/sensors/sensor1/temperature" -m "75.5" 2>/dev/null || true
        mosquitto_pub -h "$MQTT_HOST" -p "$MQTT_PORT" -t "turtle/sensors/sensor1/humidity" -m "65.2" 2>/dev/null || true
        
        # Test enclosure sensor data
        mosquitto_pub -h "$MQTT_HOST" -p "$MQTT_PORT" -t "turtle/sensors/sensor2/temperature" -m "72.8" 2>/dev/null || true
        mosquitto_pub -h "$MQTT_HOST" -p "$MQTT_PORT" -t "turtle/sensors/sensor2/humidity" -m "68.9" 2>/dev/null || true
        
        log_success "Test sensor data published"
        
        # Wait a moment for API to process
        sleep 2
        
        # Test latest readings endpoint
        test_api_endpoint "/api/latest" "Latest sensor readings"
    else
        log_warning "mosquitto_pub not available, skipping sensor data test"
    fi
}

# Function to display system status
show_status() {
    log_info "System Status Summary:"
    echo ""
    echo "API Endpoints:"
    echo "  Health Check: $API_URL/api/health"
    echo "  Latest Data: $API_URL/api/latest"
    echo "  Historical Data: $API_URL/api/history/24"
    echo "  Frontend: $API_URL/"
    echo ""
    echo "MQTT Topics:"
    echo "  Shell Temperature: turtle/sensors/sensor1/temperature"
    echo "  Shell Humidity: turtle/sensors/sensor1/humidity"
    echo "  Enclosure Temperature: turtle/sensors/sensor2/temperature"
    echo "  Enclosure Humidity: turtle/sensors/sensor2/humidity"
    echo ""
    echo "Docker Containers:"
    echo "  API: turtle-monitor-api"
    echo "  MQTT: turtle-monitor-mqtt"
}

# Main execution
main() {
    log_info "🐢 Starting Turtle Monitor API Tests"
    echo ""
    
    # Test API endpoints
    test_api_endpoint "/api/health" "API Health Check"
    test_api_endpoint "/api/latest" "Latest Sensor Readings"
    test_api_endpoint "/api/history/1" "Historical Data (1 hour)"
    test_api_endpoint "/" "Frontend Page"
    
    echo ""
    
    # Test MQTT connectivity
    test_mqtt
    
    echo ""
    
    # Test Docker containers
    test_containers
    
    echo ""
    
    # Test sensor data flow
    test_sensor_data
    
    echo ""
    
    # Show system status
    show_status
    
    log_success "🎉 API testing completed!"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --status       Show system status only"
        echo "  --api-only     Test API endpoints only"
        echo "  --mqtt-only    Test MQTT connectivity only"
        echo ""
        echo "Environment variables:"
        echo "  API_URL        API base URL (default: http://localhost:8000)"
        echo "  MQTT_HOST      MQTT broker host (default: localhost)"
        echo "  MQTT_PORT      MQTT broker port (default: 1883)"
        exit 0
        ;;
    --status)
        show_status
        exit 0
        ;;
    --api-only)
        test_api_endpoint "/api/health" "API Health Check"
        test_api_endpoint "/api/latest" "Latest Sensor Readings"
        test_api_endpoint "/" "Frontend Page"
        exit 0
        ;;
    --mqtt-only)
        test_mqtt
        test_sensor_data
        exit 0
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac 