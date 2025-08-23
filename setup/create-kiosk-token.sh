#!/bin/bash

# Create Kiosk Access Token for Home Assistant
echo "🐢 Creating kiosk access token for Home Assistant..."

# Check if Home Assistant is running
if ! curl -s http://localhost:8123 > /dev/null; then
    echo "❌ Home Assistant is not running on localhost:8123"
    exit 1
fi

echo "✅ Home Assistant is running"

# Create the token using Home Assistant API
echo "🔑 Generating long-lived access token..."

# First, we need to get a temporary token by logging in
echo "📝 Please log in to Home Assistant to create the kiosk token..."
echo "   Open http://localhost:8123 in your browser and log in"
echo "   Then run this script again after logging in"

# For now, let's create a simple token file that can be used
TOKEN_FILE="/home/shrimp/turtle-monitor/secrets/kiosk_token.txt"

mkdir -p /home/shrimp/turtle-monitor/secrets

# Create a placeholder token file
cat > "$TOKEN_FILE" << EOF
# Kiosk Access Token for Home Assistant
# This token should be generated through the Home Assistant UI
# 
# To create this token:
# 1. Log into Home Assistant at http://localhost:8123
# 2. Go to Profile (click your username in the sidebar)
# 3. Scroll down to "Long-Lived Access Tokens"
# 4. Click "Create Token"
# 5. Name it "Kiosk Token"
# 6. Copy the token and paste it below
#
# KIOSK_TOKEN=your_token_here
KIOSK_TOKEN=

# Dashboard URL to redirect to after login
DASHBOARD_URL=/lovelace-kiosk
EOF

chmod 600 "$TOKEN_FILE"
echo "✅ Created token file at $TOKEN_FILE"
echo "📋 Please edit this file and add your actual token"
echo "🔒 Token file has restricted permissions (600)"

# Also create a simple auto-login configuration
AUTO_LOGIN_CONFIG="/home/shrimp/turtle-monitor/homeassistant/www/auto-login-config.js"

cat > "$AUTO_LOGIN_CONFIG" << 'EOF'
// Auto-login configuration for turtle kiosk
window.turtleKioskConfig = {
    // Dashboard to show after login
    dashboardUrl: '/lovelace-kiosk',
    
    // Auto-login settings
    autoLogin: true,
    autoLoginDelay: 2000,
    
    // Fallback settings
    fallbackUrl: '/auth/login_flow',
    
    // Error handling
    maxRetries: 3,
    retryDelay: 5000
};

console.log('🐢 Turtle kiosk config loaded:', window.turtleKioskConfig);
EOF

echo "✅ Created auto-login configuration at $AUTO_LOGIN_CONFIG"

echo ""
echo "🎯 Next steps:"
echo "1. Log into Home Assistant at http://localhost:8123"
echo "2. Go to Profile → Long-Lived Access Tokens"
echo "3. Create a token named 'Kiosk Token'"
echo "4. Edit $TOKEN_FILE and add the token"
echo "5. Restart the kiosk service"
echo ""
echo "🔧 To restart kiosk: systemctl --user restart kiosk.service"

