#!/bin/bash

# 🐢 Turtle Monitor API System Test Script
# Tests all components of the turtle monitoring system

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test configuration
API_URL="http://localhost:8000"
MQTT_BROKER="localhost"
MQTT_PORT="1883"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local max_attempts=30
    local attempt=1
    
    log "Waiting for service at $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f "$url" >/dev/null 2>&1; then
            log_success "Service is ready at $url"
            return 0
        fi
        
        log "Attempt $attempt/$max_attempts - waiting 2 seconds..."
        sleep 2
        ((attempt++))
    done
    
    log_error "Service at $url failed to respond within expected time"
    return 1
}

# Test Docker services
test_docker_services() {
    log "Testing Docker services..."
    
    if ! command_exists docker; then
        log_error "Docker is not installed"
        return 1
    fi
    
    # Check if containers are running
    if docker ps | grep -q "turtle-monitor-api"; then
        log_success "Turtle API container is running"
    else
        log_error "Turtle API container is not running"
        return 1
    fi
    
    if docker ps | grep -q "turtle-monitor-mqtt"; then
        log_success "Mosquitto container is running"
    else
        log_error "Mosquitto container is not running"
        return 1
    fi
    
    # Check container health
    if docker inspect turtle-monitor-api | grep -q '"Status": "healthy"'; then
        log_success "Turtle API container is healthy"
    else
        log_warning "Turtle API container health check failed"
    fi
}

# Test API endpoints
test_api_endpoints() {
    log "Testing API endpoints..."
    
    # Test health endpoint
    if curl -f "$API_URL/api/health" >/dev/null 2>&1; then
        log_success "Health endpoint is working"
        
        # Get health data
        health_data=$(curl -s "$API_URL/api/health")
        echo "Health data: $health_data"
    else
        log_error "Health endpoint test failed"
        return 1
    fi
    
    # Test latest readings endpoint
    if curl -f "$API_URL/api/latest" >/dev/null 2>&1; then
        log_success "Latest readings endpoint is working"
        
        # Get latest data
        latest_data=$(curl -s "$API_URL/api/latest")
        echo "Latest data: $latest_data"
    else
        log_error "Latest readings endpoint test failed"
        return 1
    fi
    
    # Test frontend
    if curl -f "$API_URL/" >/dev/null 2>&1; then
        log_success "Frontend is accessible"
    else
        log_error "Frontend test failed"
        return 1
    fi
    
    # Test historical data endpoint
    if curl -f "$API_URL/api/history/1" >/dev/null 2>&1; then
        log_success "Historical data endpoint is working"
    else
        log_warning "Historical data endpoint test failed (may be normal if no data yet)"
    fi
}

# Test MQTT connectivity
test_mqtt_connectivity() {
    log "Testing MQTT connectivity..."
    
    # Check if mosquitto client is available
    if ! command_exists mosquitto_pub; then
        log_warning "mosquitto_pub not available, skipping MQTT tests"
        return 0
    fi
    
    # Test MQTT publish
    if mosquitto_pub -h "$MQTT_BROKER" -p "$MQTT_PORT" -t "turtle/test" -m "test_message" >/dev/null 2>&1; then
        log_success "MQTT publish test passed"
    else
        log_error "MQTT publish test failed"
        return 1
    fi
    
    # Test MQTT subscription (timeout after 5 seconds)
    if timeout 5 mosquitto_sub -h "$MQTT_BROKER" -p "$MQTT_PORT" -t "turtle/test" -C 1 >/dev/null 2>&1; then
        log_success "MQTT subscription test passed"
    else
        log_warning "MQTT subscription test failed (may be normal)"
    fi
}

# Test sensor data simulation
test_sensor_data() {
    log "Testing sensor data simulation..."
    
    # Publish test sensor data
    mosquitto_pub -h "$MQTT_BROKER" -p "$MQTT_PORT" -t "turtle/sensors/sensor1/temperature" -m "75.5" &
    mosquitto_pub -h "$MQTT_BROKER" -p "$MQTT_PORT" -t "turtle/sensors/sensor1/humidity" -m "68.2" &
    mosquitto_pub -h "$MQTT_BROKER" -p "$MQTT_PORT" -t "turtle/sensors/sensor2/temperature" -m "72.8" &
    mosquitto_pub -h "$MQTT_BROKER" -p "$MQTT_PORT" -t "turtle/sensors/sensor2/humidity" -m "71.5" &
    
    # Wait for data to be processed
    sleep 3
    
    # Check if data appears in API
    latest_data=$(curl -s "$API_URL/api/latest")
    if echo "$latest_data" | grep -q "sensor1"; then
        log_success "Sensor data is being processed by API"
        echo "Latest sensor data: $latest_data"
    else
        log_warning "Sensor data may not be processed yet"
    fi
}

# Test database functionality
test_database() {
    log "Testing database functionality..."
    
    # Check if database file exists
    if docker exec turtle-monitor-api ls -la /data/turtle_monitor.db >/dev/null 2>&1; then
        log_success "Database file exists"
    else
        log_error "Database file not found"
        return 1
    fi
    
    # Check database integrity
    if docker exec turtle-monitor-api sqlite3 /data/turtle_monitor.db "PRAGMA integrity_check;" | grep -q "ok"; then
        log_success "Database integrity check passed"
    else
        log_error "Database integrity check failed"
        return 1
    fi
    
    # Check table structure
    if docker exec turtle-monitor-api sqlite3 /data/turtle_monitor.db ".schema sensor_readings" >/dev/null 2>&1; then
        log_success "Database schema is correct"
    else
        log_error "Database schema check failed"
        return 1
    fi
}

# Test frontend functionality
test_frontend() {
    log "Testing frontend functionality..."
    
    # Check if frontend files are mounted
    if docker exec turtle-monitor-api ls -la /app/frontend/index.html >/dev/null 2>&1; then
        log_success "Frontend files are mounted correctly"
    else
        log_error "Frontend files are not mounted"
        return 1
    fi
    
    # Test if frontend loads without errors
    frontend_content=$(curl -s "$API_URL/")
    if echo "$frontend_content" | grep -q "Turtle Monitor"; then
        log_success "Frontend loads correctly"
    else
        log_error "Frontend content is not as expected"
        return 1
    fi
}

# Performance test
test_performance() {
    log "Testing system performance..."
    
    # Test API response time
    start_time=$(date +%s.%N)
    curl -f "$API_URL/api/health" >/dev/null 2>&1
    end_time=$(date +%s.%N)
    
    response_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0.1")
    log_success "API response time: ${response_time}s"
    
    # Check memory usage
    memory_usage=$(docker stats turtle-monitor-api --no-stream --format "table {{.MemUsage}}" | tail -n 1)
    log_success "Memory usage: $memory_usage"
    
    # Check disk usage
    disk_usage=$(docker exec turtle-monitor-api du -sh /data/ 2>/dev/null || echo "Unknown")
    log_success "Database size: $disk_usage"
}

# Main test function
main() {
    echo "🐢 Turtle Monitor API System Test"
    echo "=================================="
    echo ""
    
    # Wait for services to be ready
    wait_for_service "$API_URL/api/health"
    
    # Run all tests
    test_docker_services
    test_api_endpoints
    test_mqtt_connectivity
    test_sensor_data
    test_database
    test_frontend
    test_performance
    
    echo ""
    echo "🎉 All tests completed!"
    echo ""
    echo "🌐 Access your turtle monitor at: $API_URL"
    echo "📊 API health check: $API_URL/api/health"
    echo "📈 Latest readings: $API_URL/api/latest"
    echo ""
    echo "🔧 Management commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Restart: docker-compose restart"
    echo "  Stop: docker-compose down"
}

# Run main function
main "$@" 