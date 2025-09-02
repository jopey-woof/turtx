#!/bin/bash

# Reduce Chrome CPU Priority to Lower Fan Speed
# This limits Chrome's CPU usage while keeping turtle monitoring functional

echo "🔧 Reducing Chrome CPU priority for quieter operation..."

# Find Chrome processes
CHROME_PIDS=$(pgrep -f "google-chrome")

if [ -z "$CHROME_PIDS" ]; then
    echo "❌ No Chrome processes found"
    exit 1
fi

echo "Found Chrome processes: $CHROME_PIDS"

# Set Chrome processes to lower priority (nice value 10)
for pid in $CHROME_PIDS; do
    echo "Setting process $pid to lower priority..."
    renice +10 $pid 2>/dev/null || true
done

# Set CPU affinity to use only 2 cores (if available)
for pid in $CHROME_PIDS; do
    taskset -cp 0,1 $pid 2>/dev/null || true
done

echo "✅ Chrome priority reduced - should run quieter now"

# Show current nice values
echo "Chrome process priorities:"
ps -o pid,ni,comm -p $CHROME_PIDS 2>/dev/null || true