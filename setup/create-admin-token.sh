#!/bin/bash

# Create Admin Token for Kiosk User Setup
# This token is needed to create the restricted kiosk user

set -e

echo "🔑 Creating Admin Token for Kiosk Setup"
echo "======================================="

# Check Home Assistant is running
if ! curl -s http://localhost:8123 > /dev/null; then
    echo "❌ Home Assistant is not running"
    echo "   Please start Home Assistant first: docker-compose up -d"
    exit 1
fi

echo "✅ Home Assistant is running"

# Check if admin token already exists
if [ -f "/home/shrimp/turtle-monitor/.env" ] && grep -q "ADMIN_TOKEN=" "/home/shrimp/turtle-monitor/.env"; then
    echo "✅ Admin token already exists in .env file"
    echo "   You can proceed to create the kiosk user"
    exit 0
fi

echo "🔐 No admin token found. Let's create one..."

# Create the admin token creation guide
cat > /home/shrimp/turtle-monitor/security/config/admin-token-guide.md << 'EOF'
# Admin Token Creation Guide

## Step 1: Access Home Assistant
1. Open your web browser
2. Go to: http://localhost:8123
3. Log in with your admin credentials

## Step 2: Create Long-Lived Access Token
1. Click on your profile icon (bottom left)
2. Scroll down to "Long-lived access tokens"
3. Click "CREATE TOKEN"
4. Name: "Turtle Kiosk Admin Token"
5. Click "OK"
6. **COPY THE TOKEN** (you won't see it again!)

## Step 3: Add Token to Environment
Run this command and paste your token:

```bash
echo "ADMIN_TOKEN=YOUR_TOKEN_HERE" >> /home/shrimp/turtle-monitor/.env
```

## Step 4: Verify Token
Run this command to test the token:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:8123/api/
```

## Security Notes
- Keep this token secure
- This token has admin privileges
- Only use for kiosk user setup
- Consider revoking after setup is complete
EOF

echo "📋 Admin token creation guide created:"
echo "   security/config/admin-token-guide.md"

echo ""
echo "🔑 Manual Token Creation Required"
echo "================================"
echo ""
echo "Please follow these steps:"
echo ""
echo "1. Open your browser and go to: http://localhost:8123"
echo "2. Log in with your admin account"
echo "3. Go to Profile → Long-lived access tokens"
echo "4. Create a token named 'Turtle Kiosk Admin Token'"
echo "5. Copy the token"
echo ""
echo "Then run this command (replace YOUR_TOKEN_HERE with the actual token):"
echo ""
echo "echo \"ADMIN_TOKEN=YOUR_TOKEN_HERE\" >> /home/shrimp/turtle-monitor/.env"
echo ""
echo "After adding the token, run:"
echo "./setup/create-kiosk-user.sh"
echo ""
echo "🔒 Security Note: This admin token will be used only for kiosk setup"
echo "   Consider revoking it after the kiosk user is created" 