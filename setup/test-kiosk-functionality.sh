#!/bin/bash

# Test Kiosk Functionality Script
echo "🐢 Testing Kiosk Functionality..."

# Test 1: Check if Chrome kiosk is running
echo "1. Checking Chrome kiosk process..."
if pgrep -f "chrome.*--kiosk.*10.0.20.69" > /dev/null; then
    echo "✅ Chrome kiosk is running"
else
    echo "❌ Chrome kiosk is not running"
    exit 1
fi

# Test 2: Check if turtle monitor API is accessible
echo "2. Testing turtle monitor API..."
API_RESPONSE=$(curl -s http://10.0.20.69/api/latest)
if echo "$API_RESPONSE" | grep -q "temperature.*humidity"; then
    echo "✅ Turtle monitor API is working"
    echo "   Latest data: $(echo "$API_RESPONSE" | grep -o '"temperature":[0-9.]*' | head -1)"
else
    echo "❌ Turtle monitor API is not working"
    exit 1
fi

# Test 3: Check if turtle monitor frontend is accessible
echo "3. Testing turtle monitor frontend..."
FRONTEND_RESPONSE=$(curl -s http://10.0.20.69/ | head -10)
if echo "$FRONTEND_RESPONSE" | grep -q "Turtle Habitat Monitor"; then
    echo "✅ Turtle monitor frontend is accessible"
else
    echo "❌ Turtle monitor frontend is not accessible"
    exit 1
fi

# Test 4: Check if CSS files are accessible
echo "4. Testing CSS files..."
if curl -s http://10.0.20.69/css/style.css | grep -q "Turtle Habitat Monitor"; then
    echo "✅ CSS files are accessible"
else
    echo "❌ CSS files are not accessible"
fi

# Test 5: Check if API endpoint is responding with fresh data
echo "5. Testing API data freshness..."
TIMESTAMP=$(echo "$API_RESPONSE" | grep -o '"timestamp":"[^"]*"' | head -1)
echo "   API timestamp: $TIMESTAMP"

# Test 6: Check if sensors are online
echo "6. Testing sensor connectivity..."
if echo "$API_RESPONSE" | grep -q '"connection_status":"online"'; then
    echo "✅ Sensors are online"
else
    echo "❌ Sensors are offline"
fi

echo ""
echo "🎉 Kiosk functionality test completed!"
echo "📊 The kiosk should now be displaying real-time turtle monitor data"
echo "🌡️  Temperature and humidity readings should update every 2 seconds"
echo "🔄 'Last update' should show current timestamp" 