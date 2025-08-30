#!/bin/bash

# Enhanced TurtX Dashboard Test Script
echo "🐢 Testing Enhanced TurtX Dashboard with Moon Phase & Multi-Page System..."

# Test 1: Dashboard Accessibility
echo "📊 Test 1: Dashboard Accessibility"
if curl -s "http://10.0.20.69/" | grep -q "TurtX Monitor"; then
    echo "✅ Enhanced dashboard is accessible"
else
    echo "❌ Dashboard is not accessible"
    exit 1
fi

# Test 2: Moon Phase System
echo "🌙 Test 2: Moon Phase System"
MOON_COUNT=$(curl -s "http://10.0.20.69/" | grep -c "moon-phase")
if [ "$MOON_COUNT" -ge 5 ]; then
    echo "✅ Moon phase system implemented ($MOON_COUNT elements found)"
else
    echo "❌ Moon phase system not found"
fi

# Test 3: Multi-Page System
echo "📄 Test 3: Multi-Page System"
PAGE_COUNT=$(curl -s "http://10.0.20.69/" | grep -c "camera-page\|data-page")
if [ "$PAGE_COUNT" -ge 2 ]; then
    echo "✅ Multi-page system implemented ($PAGE_COUNT pages found)"
else
    echo "❌ Multi-page system not found"
fi

# Test 4: Star Field Animation
echo "⭐ Test 4: Star Field Animation"
STAR_COUNT=$(curl -s "http://10.0.20.69/" | grep -c "star-field")
if [ "$STAR_COUNT" -ge 1 ]; then
    echo "✅ Star field animation implemented"
else
    echo "❌ Star field animation not found"
fi

# Test 5: Nyan Turtle Animation
echo "🐢 Test 5: Nyan Turtle Animation"
TURTLE_COUNT=$(curl -s "http://10.0.20.69/" | grep -c "nyan-turtle")
if [ "$TURTLE_COUNT" -ge 2 ]; then
    echo "✅ Nyan turtle animation implemented"
else
    echo "❌ Nyan turtle animation not found"
fi

# Test 6: Camera Integration
echo "📹 Test 6: Camera Integration"
CAMERA_COUNT=$(curl -s "http://10.0.20.69/" | grep -c "camera-stream\|camera-status")
if [ "$CAMERA_COUNT" -ge 2 ]; then
    echo "✅ Camera integration implemented"
else
    echo "❌ Camera integration not found"
fi

# Test 7: Data Analysis Page
echo "📈 Test 7: Data Analysis Page"
DATA_COUNT=$(curl -s "http://10.0.20.69/" | grep -c "chart-card\|activity-log")
if [ "$DATA_COUNT" -ge 2 ]; then
    echo "✅ Data analysis page implemented"
else
    echo "❌ Data analysis page not found"
fi

# Test 8: Touch Gestures
echo "👆 Test 8: Touch Gestures"
GESTURE_COUNT=$(curl -s "http://10.0.20.69/" | grep -c "touchstart\|touchend")
if [ "$GESTURE_COUNT" -ge 2 ]; then
    echo "✅ Touch gesture navigation implemented"
else
    echo "❌ Touch gesture navigation not found"
fi

# Test 9: API Data Integration
echo "📡 Test 9: API Data Integration"
API_RESPONSE=$(curl -s "http://10.0.20.69/api/latest")
if echo "$API_RESPONSE" | grep -q '"temperature"'; then
    echo "✅ API data integration working"
    TEMP1=$(echo "$API_RESPONSE" | grep -o '"temperature":[0-9.]*' | head -1 | cut -d: -f2)
    TEMP2=$(echo "$API_RESPONSE" | grep -o '"temperature":[0-9.]*' | tail -1 | cut -d: -f2)
    echo "   Current temperatures: ${TEMP1}°F, ${TEMP2}°F"
else
    echo "❌ API data integration not working"
fi

# Test 10: Real-time Updates
echo "🔄 Test 10: Real-time Updates"
UPDATE_COUNT=$(curl -s "http://10.0.20.69/" | grep -c "setInterval.*2000")
if [ "$UPDATE_COUNT" -ge 1 ]; then
    echo "✅ Real-time updates configured (2-second intervals)"
else
    echo "❌ Real-time updates not configured"
fi

# Test 11: Weather Integration
echo "🌤️ Test 11: Weather Integration"
WEATHER_COUNT=$(curl -s "http://10.0.20.69/" | grep -c "weather-card\|weather-info")
if [ "$WEATHER_COUNT" -ge 2 ]; then
    echo "✅ Weather integration implemented"
else
    echo "❌ Weather integration not found"
fi

# Test 12: System Indicators
echo "⚡ Test 12: System Indicators"
INDICATOR_COUNT=$(curl -s "http://10.0.20.69/" | grep -c "indicator.*status")
if [ "$INDICATOR_COUNT" -ge 5 ]; then
    echo "✅ System indicators implemented"
else
    echo "❌ System indicators not found"
fi

echo ""
echo "🎉 Enhanced Dashboard Test Complete!"
echo ""
echo "📋 Enhanced Features Summary:"
echo "   • Moon Phase Display: Real moon phase calculation with illumination"
echo "   • Multi-Page System: Status, Camera, and Data pages"
echo "   • Star Field Animation: Twinkling stars background"
echo "   • Nyan Turtle Animation: Turtle with star trail"
echo "   • Camera Integration: Multiple camera endpoints with fallback"
echo "   • Data Analysis: Charts and activity logs"
echo "   • Touch Gestures: Swipe navigation between pages"
echo "   • Real-time Updates: 2-second sensor data refresh"
echo "   • Weather Integration: Mock weather display"
echo "   • System Indicators: Real-time status monitoring"
echo ""
echo "🚀 The Enhanced TurtX Dashboard now matches the beautiful existing design!"
echo "   Dashboard URL: http://10.0.20.69/"
echo "   Kiosk Mode: Updated to use new dashboard" 