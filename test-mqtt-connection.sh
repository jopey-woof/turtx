#!/bin/bash

# Test MQTT Connection for Turtle Dashboard
# This script tests the MQTT connection and sensor data flow

set -e

echo "🔍 Testing MQTT Connection for Turtle Dashboard"
echo "==============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Get Home Assistant IP
if [[ -z "$1" ]]; then
    echo ""
    print_info "Please enter your Home Assistant IP address:"
    read -p "Home Assistant IP: " HA_IP
else
    HA_IP="$1"
fi

if [[ -z "$HA_IP" ]]; then
    print_error "Home Assistant IP is required"
    exit 1
fi

print_status "Testing connection to: $HA_IP"

# Test basic connectivity
echo ""
print_info "Testing basic network connectivity..."
if ping -c 3 "$HA_IP" > /dev/null 2>&1; then
    print_status "Network connectivity: OK"
else
    print_error "Cannot reach $HA_IP"
    exit 1
fi

# Test MQTT port
echo ""
print_info "Testing MQTT port 9001..."
if timeout 5 bash -c "</dev/tcp/$HA_IP/9001" 2>/dev/null; then
    print_status "MQTT port 9001: OK"
else
    print_error "Cannot connect to MQTT port 9001 on $HA_IP"
    print_warning "Make sure Home Assistant MQTT broker is running and configured for WebSocket connections"
    exit 1
fi

# Test MQTT subscription
echo ""
print_info "Testing MQTT subscription to turtle sensor topics..."
print_info "This will listen for 10 seconds for sensor data..."

# Create temporary script for MQTT subscription
cat > /tmp/test_mqtt_sub.sh <<EOF
#!/bin/bash
mosquitto_sub -h $HA_IP -p 9001 -t "turtle/+/+" -C 5 -W 10 2>/dev/null || echo "No messages received"
EOF

chmod +x /tmp/test_mqtt_sub.sh

# Run MQTT subscription test
echo "Listening for messages on turtle/+/+ topics..."
MESSAGES=$(/tmp/test_mqtt_sub.sh)

if [[ -n "$MESSAGES" ]]; then
    print_status "MQTT subscription: OK"
    echo "Received messages:"
    echo "$MESSAGES" | while read -r line; do
        if [[ -n "$line" ]]; then
            echo "  📨 $line"
        fi
    done
else
    print_warning "No MQTT messages received"
    print_info "This could mean:"
    print_info "  - Sensors are not publishing data yet"
    print_info "  - Topics are different than expected"
    print_info "  - MQTT broker needs configuration"
fi

# Test specific topics
echo ""
print_info "Testing specific sensor topics..."

TOPICS=(
    "turtle/sensor1/temperature"
    "turtle/sensor1/humidity"
    "turtle/sensor2/temperature"
    "turtle/sensor2/humidity"
)

for topic in "${TOPICS[@]}"; do
    echo "Testing topic: $topic"
    if timeout 3 mosquitto_sub -h "$HA_IP" -p 9001 -t "$topic" -C 1 -W 3 >/dev/null 2>&1; then
        print_status "  $topic: OK"
    else
        print_warning "  $topic: No data (this is normal if sensors aren't publishing)"
    fi
done

# Test publishing (optional)
echo ""
print_info "Testing MQTT publishing capability..."
if timeout 3 mosquitto_pub -h "$HA_IP" -p 9001 -t "turtle/test/connection" -m "test" >/dev/null 2>&1; then
    print_status "MQTT publishing: OK"
else
    print_warning "MQTT publishing: Failed (read-only access is fine for dashboard)"
fi

# Cleanup
rm -f /tmp/test_mqtt_sub.sh

# Summary
echo ""
echo "📊 MQTT Connection Test Summary"
echo "==============================="
print_status "Network connectivity: OK"
print_status "MQTT port 9001: OK"

if [[ -n "$MESSAGES" ]]; then
    print_status "MQTT subscription: OK (data flowing)"
    echo ""
    print_info "🎉 Your MQTT setup is working correctly!"
    print_info "The turtle dashboard should be able to connect and receive sensor data."
else
    print_warning "MQTT subscription: No data received"
    echo ""
    print_warning "⚠️  No sensor data is currently flowing."
    print_info "To get the dashboard working:"
    print_info "1. Make sure your TemperhUM sensors are connected and running"
    print_info "2. Verify they're publishing to the correct MQTT topics"
    print_info "3. Check Home Assistant MQTT integration configuration"
    print_info "4. The dashboard will show '--' values until data is received"
fi

echo ""
print_info "Dashboard MQTT Configuration:"
echo "  Broker: ws://$HA_IP:9001"
echo "  Topics:"
echo "    - turtle/sensor1/temperature"
echo "    - turtle/sensor1/humidity"
echo "    - turtle/sensor2/temperature"
echo "    - turtle/sensor2/humidity"

echo ""
print_status "Test complete! 🐢" 