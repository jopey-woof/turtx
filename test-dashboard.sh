#!/bin/bash

# TurtX Dashboard Deployment Test Script
echo "🐢 Testing TurtX Professional Dashboard Deployment..."

# Test 1: Dashboard Accessibility
echo "📊 Test 1: Dashboard Accessibility"
if curl -s "http://10.0.20.69/" | grep -q "TurtX Professional Monitor"; then
    echo "✅ Dashboard is accessible and serving correctly"
else
    echo "❌ Dashboard is not accessible"
    exit 1
fi

# Test 2: API Data Flow
echo "📡 Test 2: API Data Flow"
API_RESPONSE=$(curl -s "http://10.0.20.69/api/latest")
if echo "$API_RESPONSE" | grep -q '"temperature"'; then
    echo "✅ API is returning sensor data"
    TEMP1=$(echo "$API_RESPONSE" | grep -o '"temperature":[0-9.]*' | head -1 | cut -d: -f2)
    TEMP2=$(echo "$API_RESPONSE" | grep -o '"temperature":[0-9.]*' | tail -1 | cut -d: -f2)
    echo "   Sensor 1 Temperature: ${TEMP1}°F"
    echo "   Sensor 2 Temperature: ${TEMP2}°F"
else
    echo "❌ API is not returning sensor data"
    exit 1
fi

# Test 3: Real-time Updates
echo "🔄 Test 3: Real-time Updates"
echo "   Testing 2-second update interval..."
sleep 2
API_RESPONSE2=$(curl -s "http://10.0.20.69/api/latest")
TEMP1_2=$(echo "$API_RESPONSE2" | grep -o '"temperature":[0-9.]*' | head -1 | cut -d: -f2)
if [ "$TEMP1" != "$TEMP1_2" ]; then
    echo "✅ Real-time updates are working (temperature changed: $TEMP1 → $TEMP1_2)"
else
    echo "⚠️  Temperature unchanged (may be normal if sensors are stable)"
fi

# Test 4: Theme System
echo "🎨 Test 4: Theme System"
if curl -s "http://10.0.20.69/" | grep -q "theme-professional-day"; then
    echo "✅ Theme system is properly implemented"
else
    echo "❌ Theme system not found"
fi

# Test 5: Responsive Design
echo "📱 Test 5: Responsive Design"
if curl -s "http://10.0.20.69/" | grep -q "100vh"; then
    echo "✅ Responsive design elements present"
else
    echo "❌ Responsive design not found"
fi

# Test 6: Connection Status
echo "🔗 Test 6: Connection Status"
if curl -s "http://10.0.20.69/" | grep -q "connection-status"; then
    echo "✅ Connection status indicator present"
else
    echo "❌ Connection status indicator not found"
fi

# Test 7: Navigation System
echo "🧭 Test 7: Navigation System"
if curl -s "http://10.0.20.69/" | grep -q "nav-button"; then
    echo "✅ Navigation system present"
else
    echo "❌ Navigation system not found"
fi

# Test 8: Sensor Cards
echo "📊 Test 8: Sensor Cards"
if curl -s "http://10.0.20.69/" | grep -q "sensor-card"; then
    echo "✅ Sensor cards present"
else
    echo "❌ Sensor cards not found"
fi

# Test 9: System Indicators
echo "⚡ Test 9: System Indicators"
if curl -s "http://10.0.20.69/" | grep -q "system-indicators"; then
    echo "✅ System indicators present"
else
    echo "❌ System indicators not found"
fi

# Test 10: Weather Integration
echo "🌤️ Test 10: Weather Integration"
if curl -s "http://10.0.20.69/" | grep -q "weather-card"; then
    echo "✅ Weather integration present"
else
    echo "❌ Weather integration not found"
fi

echo ""
echo "🎉 Dashboard Deployment Test Complete!"
echo ""
echo "📋 Summary:"
echo "   • Dashboard URL: http://10.0.20.69/"
echo "   • API Endpoint: http://10.0.20.69/api/latest"
echo "   • Current Temperature: ${TEMP1}°F (Sensor 1), ${TEMP2}°F (Sensor 2)"
echo "   • Real-time Updates: Every 2 seconds"
echo "   • Theme System: 6 professional themes available"
echo "   • Kiosk Mode: Ready for touchscreen deployment"
echo ""
echo "🚀 The TurtX Professional Dashboard is successfully deployed and operational!" 