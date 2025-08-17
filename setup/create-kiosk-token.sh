#!/bin/bash

# Create Long-Lived Access Token for Turtle Kiosk Auto-Login
# This token will allow Chrome to access HA without showing login screen

echo "🐢 Creating Long-Lived Access Token for Turtle Kiosk..."

# Wait for Home Assistant to be fully ready
echo "⏳ Waiting for Home Assistant..."
while ! curl -s http://localhost:8123 > /dev/null; do
    sleep 5
done

echo "✅ Home Assistant is ready"
echo ""
echo "📋 INSTRUCTIONS:"
echo "1. Open a browser and go to: http://$(hostname -I | awk {print }):8123"
echo "2. Login with your credentials (shrimp/shrimp)"
echo "3. Click your profile (bottom left)"
echo "4. Scroll down to \"Long-lived access tokens\""
echo "5. Click \"CREATE TOKEN\""
echo "6. Name it: \"Turtle Kiosk Token\""
echo "7. Copy the token and paste it below"
echo ""

# Prompt for the token
read -p "🔑 Paste your Long-Lived Access Token here: " KIOSK_TOKEN

if [ -z "$KIOSK_TOKEN" ]; then
    echo "❌ No token provided. Please run this script again."
    exit 1
fi

# Save the token securely
echo "KIOSK_TOKEN=$KIOSK_TOKEN" >> /home/shrimp/turtle-monitor/.env
chmod 600 /home/shrimp/turtle-monitor/.env

echo "✅ Token saved successfully!"
echo "🔐 Token stored in .env file with secure permissions"
echo ""
echo "Next: Restart the kiosk service to use the token"
echo "Run: sudo systemctl restart kiosk.service"

