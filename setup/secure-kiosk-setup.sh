#!/bin/bash

# Turtle Kiosk Security-First Setup Script
# Implements minimal permission user with comprehensive security controls

set -e

echo "🐢 Turtle Kiosk Security Setup - Phase 1: Security Assessment"
echo "=============================================================="

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then
    echo "❌ This script should NOT be run as root for security reasons"
    echo "   Run as regular user: ./setup/secure-kiosk-setup.sh"
    exit 1
fi

# Verify we're in the correct directory
if [ ! -f "docker/docker-compose.yml" ]; then
    echo "❌ Please run this script from the turtle-monitor directory"
    exit 1
fi

echo "✅ Security check passed - running as non-root user"
echo "✅ Located in turtle-monitor directory"

# Create security directories
echo "🔒 Creating security directories..."
mkdir -p /home/shrimp/turtle-monitor/security/{logs,config,monitoring}
mkdir -p /home/shrimp/turtle-monitor/kiosk/secure

# Set proper permissions
chmod 700 /home/shrimp/turtle-monitor/security
chmod 600 /home/shrimp/turtle-monitor/security/config/*
chmod 644 /home/shrimp/turtle-monitor/security/logs/*

echo "✅ Security directories created with proper permissions"

# Check current Home Assistant status
echo "🔍 Checking Home Assistant status..."
if curl -s http://localhost:8123 > /dev/null; then
    echo "✅ Home Assistant is running"
else
    echo "❌ Home Assistant is not running"
    echo "   Please start Home Assistant first: docker-compose up -d"
    exit 1
fi

echo ""
echo "🐢 Phase 1 Complete: Security Assessment"
echo "🐢 Next: Creating minimal permission kiosk user"
echo ""
echo "Run the next phase: ./setup/create-kiosk-user.sh" 