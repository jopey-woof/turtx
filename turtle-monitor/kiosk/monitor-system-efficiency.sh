#!/bin/bash

# TurtX System Efficiency Monitor
# Monitors system resources and prevents fan overload

LOG_FILE="/home/shrimp/turtle-monitor/logs/efficiency.log"
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log with timestamp
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to get CPU temperature
get_cpu_temp() {
    if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        temp=$(cat /sys/class/thermal/thermal_zone0/temp)
        echo $((temp / 1000))
    else
        echo "0"
    fi
}

# Function to get CPU usage
get_cpu_usage() {
    top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
}

# Function to optimize if needed
optimize_system() {
    local reason="$1"
    log_message "OPTIMIZATION TRIGGERED: $reason"
    
    # Lower Chrome priority if running
    CHROME_PID=$(pgrep -f chromium-browser | head -1)
    if [ -n "$CHROME_PID" ]; then
        renice 15 $CHROME_PID >/dev/null 2>&1 || true
        log_message "Reduced Chrome priority (PID: $CHROME_PID)"
    fi
    
    # Set CPU governor to powersave
    echo powersave | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor >/dev/null 2>&1 || true
    
    # Clear system caches if memory is high
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$MEM_USAGE" -gt 80 ]; then
        sudo sync
        sudo sysctl vm.drop_caches=1 >/dev/null 2>&1 || true
        log_message "Cleared system caches (Memory usage: ${MEM_USAGE}%)"
    fi
}

log_message "Starting TurtX efficiency monitor..."

while true; do
    # Get system metrics
    CPU_TEMP=$(get_cpu_temp)
    CPU_USAGE=$(get_cpu_usage)
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    
    # Check if optimization is needed
    NEEDS_OPTIMIZATION=false
    REASON=""
    
    # Temperature check (adjust threshold as needed)
    if [ "$CPU_TEMP" -gt 70 ]; then
        NEEDS_OPTIMIZATION=true
        REASON="High CPU temperature: ${CPU_TEMP}°C"
    fi
    
    # CPU usage check
    if (( $(echo "$CPU_USAGE > 50" | bc -l 2>/dev/null || echo "0") )); then
        NEEDS_OPTIMIZATION=true
        REASON="High CPU usage: ${CPU_USAGE}%"
    fi
    
    # Memory usage check
    if [ "$MEM_USAGE" -gt 85 ]; then
        NEEDS_OPTIMIZATION=true
        REASON="High memory usage: ${MEM_USAGE}%"
    fi
    
    # Optimize if needed
    if [ "$NEEDS_OPTIMIZATION" = true ]; then
        optimize_system "$REASON"
    fi
    
    # Log status every 5 minutes
    MINUTE=$(date +%M)
    if [ $((MINUTE % 5)) -eq 0 ] && [ "$(date +%S)" -lt 30 ]; then
        log_message "Status - CPU: ${CPU_USAGE}%, Temp: ${CPU_TEMP}°C, Memory: ${MEM_USAGE}%"
    fi
    
    # Check every 30 seconds
    sleep 30
done