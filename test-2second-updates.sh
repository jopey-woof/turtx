#!/bin/bash

echo "🐢 Testing 2-Second Update Frequency"
echo "===================================="

echo -e "\n📊 Monitoring sensor updates for 10 seconds..."
echo "Checking every 2 seconds to verify update frequency:"

for i in {1..5}; do
    echo -e "\n--- Reading $i ---"
    echo "Time: $(date '+%H:%M:%S')"
    
    # Get API data
    API_DATA=$(curl -s http://localhost/api/latest)
    
    # Extract timestamps
    API_TIME=$(echo "$API_DATA" | grep -o '"timestamp":"[^"]*"' | cut -d'"' -f4 | cut -d'T' -f2 | cut -d'.' -f1)
    SENSOR_TIME=$(echo "$API_DATA" | grep -o '"sensor1".*"timestamp":"[^"]*"' | cut -d'"' -f8 | cut -d' ' -f2)
    
    # Extract values
    TEMP1=$(echo "$API_DATA" | grep -o '"sensor1".*"temperature":[0-9.]*' | cut -d':' -f2 | cut -d',' -f1)
    HUM1=$(echo "$API_DATA" | grep -o '"sensor1".*"humidity":[0-9.]*' | cut -d':' -f2 | cut -d',' -f1)
    TEMP2=$(echo "$API_DATA" | grep -o '"sensor2".*"temperature":[0-9.]*' | cut -d':' -f2 | cut -d',' -f1)
    HUM2=$(echo "$API_DATA" | grep -o '"sensor2".*"humidity":[0-9.]*' | cut -d':' -f2 | cut -d',' -f1)
    
    echo "API Time: $API_TIME"
    echo "Sensor Time: $SENSOR_TIME"
    echo "Sensor1: ${TEMP1}°F, ${HUM1}%"
    echo "Sensor2: ${TEMP2}°F, ${HUM2}%"
    
    # Store previous values for comparison
    if [ $i -gt 1 ]; then
        if [ "$PREV_TEMP1" != "$TEMP1" ] || [ "$PREV_TEMP2" != "$TEMP2" ]; then
            echo "✅ Values changed!"
        else
            echo "⚠️  Values same (normal for stable environment)"
        fi
    fi
    
    PREV_TEMP1=$TEMP1
    PREV_TEMP2=$TEMP2
    
    sleep 2
done

echo -e "\n🎉 2-Second Update Test Complete!"
echo "Expected: Updates every ~2 seconds"
echo "Actual: Check timestamps above for frequency"
echo -e "\n📈 Benefits for cooling systems:"
echo "• Much faster response to temperature changes"
echo "• Quick feedback for cooling adjustments"
echo "• Real-time monitoring of temperature trends"
echo "• Better control over turtle habitat conditions" 