#!/bin/bash

# Debug script to check remote system structure

echo "=== Debug Remote System ==="

# Test SSH connection and check directory structure
ssh shrimp@10.0.20.69 << 'EOF'
echo "Current directory: $(pwd)"
echo "Home directory contents:"
ls -la /home/shrimp/

echo ""
echo "Checking if turtx directory exists:"
if [ -d "/home/shrimp/turtx" ]; then
    echo "✅ turtx directory exists"
    echo "turtx contents:"
    ls -la /home/shrimp/turtx/
    
    echo ""
    echo "Checking turtle-monitor directory:"
    if [ -d "/home/shrimp/turtx/turtle-monitor" ]; then
        echo "✅ turtle-monitor directory exists"
        echo "turtle-monitor contents:"
        ls -la /home/shrimp/turtx/turtle-monitor/
        
        echo ""
        echo "Checking deployment directory:"
        if [ -d "/home/shrimp/turtx/turtle-monitor/deployment" ]; then
            echo "✅ deployment directory exists"
            echo "deployment contents:"
            ls -la /home/shrimp/turtx/turtle-monitor/deployment/
        else
            echo "❌ deployment directory does not exist"
        fi
    else
        echo "❌ turtle-monitor directory does not exist"
    fi
else
    echo "❌ turtx directory does not exist"
fi

echo ""
echo "Docker status:"
docker --version 2>/dev/null || echo "Docker not installed"
docker-compose --version 2>/dev/null || echo "Docker-compose not installed"

echo ""
echo "Current user: $(whoami)"
echo "Current working directory: $(pwd)"
EOF

echo "=== Debug Complete ===" 