#!/bin/bash

# Automatically create Long-Lived Access Token for Turtle Kiosk
echo "🐢 Creating Kiosk Token Automatically..."

# Login and get auth token
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8123/auth/login_flow \
  -H "Content-Type: application/json" \
  -d {handler: [homeassistant, null], username: shrimp, password: shrimp})

echo "Login response: $LOGIN_RESPONSE"

# Extract the access token from login
if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o access_token:[^]*' | cut -d' -f4)
    
    if [ ! -z "$ACCESS_TOKEN" ]; then
        echo "✅ Successfully obtained access token!"
        echo "KIOSK_TOKEN=$ACCESS_TOKEN" >> /home/shrimp/turtle-monitor/.env
        chmod 600 /home/shrimp/turtle-monitor/.env
        echo "🔐 Token saved to .env file"
        echo "🚀 Ready to restart kiosk service!"
    else
        echo "❌ Could not extract access token"
    fi
else
    echo "❌ Login failed. Response: $LOGIN_RESPONSE"
fi

