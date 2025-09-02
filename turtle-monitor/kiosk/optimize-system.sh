#!/bin/bash

# TurtX System Optimization Script
# Reduces CPU load and fan noise for kiosk operation

echo "🔧 Optimizing TurtX system for quiet operation..."

# CPU optimizations
echo "⚡ Applying CPU optimizations..."

# Disable CPU turbo boost to reduce heat (requires root)
echo shrimp | sudo -S sh -c "echo 1 > /sys/devices/system/cpu/intel_pstate/no_turbo" 2>/dev/null || echo "Turbo boost control not available"

# Set CPU governor to powersave
echo shrimp | sudo -S sh -c "echo powersave > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor" 2>/dev/null || echo "Governor control not available"

# Reduce swappiness to minimize disk I/O
echo shrimp | sudo -S sysctl vm.swappiness=10 || true

# Optimize I/O scheduler for SSD
echo shrimp | sudo -S sh -c "echo mq-deadline > /sys/block/*/queue/scheduler" 2>/dev/null || true

echo "✅ System optimizations applied"

# Docker optimizations
echo "🐳 Optimizing Docker containers..."
docker update --cpus="1.0" --memory="1g" homeassistant 2>/dev/null || echo "Docker optimization skipped"

# Service optimizations
echo "🚀 Optimizing services..."
echo shrimp | sudo -S systemctl disable bluetooth.service 2>/dev/null || true
echo shrimp | sudo -S systemctl disable cups.service 2>/dev/null || true
echo shrimp | sudo -S systemctl disable avahi-daemon.service 2>/dev/null || true

echo "✅ TurtX system optimized for quiet operation!"

# Show current status
echo "Current CPU load:"
uptime
echo "Current temperature (if available):"
sensors 2>/dev/null | grep -i temp | head -3 || echo "Temperature sensors not available"