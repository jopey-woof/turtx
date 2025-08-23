#!/bin/bash

echo "🐢 Testing Sensor Updates"
echo "========================"

echo -e "\n📊 Checking sensor data updates..."

# Get initial reading
echo "Initial reading:"
INITIAL=$(curl -s http://localhost/api/latest)
echo "$INITIAL" | grep -o "timestamp.*" | head -3

# Wait for updates
echo -e "\n⏳ Waiting 20 seconds for sensor updates..."
sleep 20

# Get updated reading
echo -e "\nUpdated reading:"
UPDATED=$(curl -s http://localhost/api/latest)
echo "$UPDATED" | grep -o "timestamp.*" | head -3

# Compare timestamps
INITIAL_TIME=$(echo "$INITIAL" | grep -o '"timestamp":"[^"]*"' | head -1 | cut -d'"' -f4)
UPDATED_TIME=$(echo "$UPDATED" | grep -o '"timestamp":"[^"]*"' | head -1 | cut -d'"' -f4)

echo -e "\n📈 Analysis:"
echo "Initial API timestamp: $INITIAL_TIME"
echo "Updated API timestamp: $UPDATED_TIME"

# Check if timestamps are different
if [ "$INITIAL_TIME" != "$UPDATED_TIME" ]; then
    echo "✅ API timestamps are updating"
else
    echo "❌ API timestamps are not updating"
fi

# Check sensor timestamps
SENSOR1_INITIAL=$(echo "$INITIAL" | grep -o '"sensor1".*"timestamp":"[^"]*"' | cut -d'"' -f8)
SENSOR1_UPDATED=$(echo "$UPDATED" | grep -o '"sensor1".*"timestamp":"[^"]*"' | cut -d'"' -f8)

echo "Sensor1 initial: $SENSOR1_INITIAL"
echo "Sensor1 updated: $SENSOR1_UPDATED"

if [ "$SENSOR1_INITIAL" != "$SENSOR1_UPDATED" ]; then
    echo "✅ Sensor1 timestamps are updating"
else
    echo "❌ Sensor1 timestamps are not updating"
fi

# Check temperature values
TEMP1_INITIAL=$(echo "$INITIAL" | grep -o '"sensor1".*"temperature":[0-9.]*' | cut -d':' -f2 | cut -d',' -f1)
TEMP1_UPDATED=$(echo "$UPDATED" | grep -o '"sensor1".*"temperature":[0-9.]*' | cut -d':' -f2 | cut -d',' -f1)

echo "Sensor1 temp initial: $TEMP1_INITIAL"
echo "Sensor1 temp updated: $TEMP1_UPDATED"

if [ "$TEMP1_INITIAL" != "$TEMP1_UPDATED" ]; then
    echo "✅ Sensor1 temperature values are updating"
else
    echo "⚠️  Sensor1 temperature values are the same (this might be normal if environment is stable)"
fi

echo -e "\n🎉 Sensor Update Test Complete!"
echo "If you see ✅ marks above, your sensors are working correctly!" 