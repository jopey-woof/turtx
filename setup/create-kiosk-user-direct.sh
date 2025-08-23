#!/bin/bash

# Direct Kiosk User Creation - Modify Home Assistant Auth File
# This script directly adds the kiosk user to the Home Assistant auth storage

set -e

echo "🐢 Direct Kiosk User Creation"
echo "============================="

# Check if we're in the right directory
if [ ! -f "docker/docker-compose.yml" ]; then
    echo "❌ Please run this script from the turtle-monitor directory"
    exit 1
fi

echo "✅ Located in turtle-monitor directory"

# Check if Home Assistant is running
if ! curl -s http://localhost:8123 > /dev/null; then
    echo "❌ Home Assistant is not running"
    exit 1
fi

echo "✅ Home Assistant is running"

# Get the Home Assistant container ID
CONTAINER_ID=$(docker ps -q --filter "name=homeassistant")
if [ -z "$CONTAINER_ID" ]; then
    echo "❌ Home Assistant container not found"
    exit 1
fi

echo "✅ Found Home Assistant container: $CONTAINER_ID"

# Create a Python script to add the kiosk user directly to the auth file
echo ""
echo "👤 Creating kiosk user directly in Home Assistant..."

cat > /home/shrimp/turtle-monitor/security/config/add-kiosk-user-direct.py << 'EOF'
#!/usr/bin/env python3
"""
Add kiosk user directly to Home Assistant auth file
"""

import os
import sys
import json
import hashlib
import secrets
import subprocess

def add_kiosk_user():
    """Add kiosk user directly to Home Assistant auth file"""
    
    # Get container ID
    try:
        result = subprocess.run(['docker', 'ps', '-q', '--filter', 'name=homeassistant'], 
                              capture_output=True, text=True, check=True)
        container_id = result.stdout.strip()
        if not container_id:
            print("❌ Home Assistant container not found")
            return False
    except subprocess.CalledProcessError:
        print("❌ Error finding Home Assistant container")
        return False
    
    print(f"✅ Found container: {container_id}")
    
    # Read current auth file
    try:
        result = subprocess.run(['docker', 'exec', container_id, 'cat', '/config/.storage/auth'], 
                              capture_output=True, text=True, check=True)
        auth_data = json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"❌ Error reading auth file: {e}")
        return False
    
    # Check if kiosk user already exists
    users = auth_data.get('data', {}).get('users', [])
    for user in users:
        if user.get('username') == 'turtle_kiosk':
            print("✅ Kiosk user already exists")
            return True
    
    print("Creating kiosk user...")
    
    # Create password hash
    password = 'turtle_kiosk_secure_2024!'
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    
    # Create new user
    new_user = {
        "id": f"kiosk_{secrets.token_hex(8)}",
        "username": "turtle_kiosk",
        "name": "Turtle Kiosk",
        "is_owner": False,
        "is_active": True,
        "system_generated": False,
        "group_ids": ["system-readonly"],
        "credentials": [
            {
                "id": f"kiosk_cred_{secrets.token_hex(8)}",
                "auth_provider_type": "homeassistant",
                "auth_provider_id": None,
                "data": {
                    "username": "turtle_kiosk",
                    "password": password_hash.hex(),
                    "salt": salt
                }
            }
        ]
    }
    
    # Add user to auth data
    users.append(new_user)
    auth_data['data']['users'] = users
    
    # Create backup
    try:
        subprocess.run(['docker', 'exec', container_id, 'cp', '/config/.storage/auth', '/config/.storage/auth.backup'], 
                      check=True)
        print("✅ Auth file backed up")
    except subprocess.CalledProcessError:
        print("⚠️  Could not create backup")
    
    # Write updated auth data
    try:
        auth_json = json.dumps(auth_data, indent=2)
        subprocess.run(['docker', 'exec', '-i', container_id, 'tee', '/config/.storage/auth'], 
                      input=auth_json, text=True, check=True)
        print("✅ Auth file updated")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error writing auth file: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if add_kiosk_user():
        print("🎉 Kiosk user created successfully!")
        print("   Username: turtle_kiosk")
        print("   Password: turtle_kiosk_secure_2024!")
        print("   Permissions: Dashboard viewing only")
    else:
        print("❌ Failed to create kiosk user")
        sys.exit(1)
EOF

chmod +x /home/shrimp/turtle-monitor/security/config/add-kiosk-user-direct.py

# Run the user creation script
cd /home/shrimp/turtle-monitor
python3 security/config/add-kiosk-user-direct.py

# Restart Home Assistant to apply the changes
echo ""
echo "🔄 Restarting Home Assistant to apply user changes..."

docker restart $CONTAINER_ID

echo "✅ Home Assistant restarted"

# Wait for Home Assistant to start
echo "⏳ Waiting for Home Assistant to start..."
sleep 30

# Test the kiosk user
echo ""
echo "🧪 Testing kiosk user authentication..."

KIOSK_LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8123/auth/login_flow \
  -H "Content-Type: application/json" \
  -d '{"username": "turtle_kiosk", "password": "turtle_kiosk_secure_2024!", "client_id": "test"}')

if echo "$KIOSK_LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "✅ Kiosk user authentication successful!"
    KIOSK_TOKEN=$(echo "$KIOSK_LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Access token obtained: ${KIOSK_TOKEN:0:20}..."
else
    echo "❌ Kiosk user authentication failed"
    echo "   Response: $KIOSK_LOGIN_RESPONSE"
fi

# Update the kiosk startup script to use the auto-login page
echo ""
echo "🔄 Updating kiosk startup script..."

# Update the kiosk startup script to use the auto-login page
sed -i 's|http://localhost:8123/local/simple-kiosk-setup.html|http://localhost:8123/local/auto-kiosk.html|g' /home/shrimp/turtle-monitor/kiosk/start-kiosk-stable.sh

echo "✅ Kiosk startup script updated"

# Final instructions
echo ""
echo "🎉 Direct Kiosk User Creation Complete!"
echo "======================================="
echo ""
echo "✅ Kiosk user created directly in Home Assistant"
echo "✅ Home Assistant restarted"
echo "✅ Kiosk startup script updated"
echo ""
echo "🔒 Kiosk User Details:"
echo "   Username: turtle_kiosk"
echo "   Password: turtle_kiosk_secure_2024!"
echo "   Permissions: Dashboard viewing only"
echo ""
echo "🚀 Next Steps:"
echo "1. Restart the kiosk service:"
echo "   systemctl --user restart kiosk.service"
echo ""
echo "2. The kiosk should now work automatically!"
echo ""
echo "📊 Monitor kiosk access:"
echo "   tail -f /home/shrimp/turtle-monitor/security/logs/kiosk-access.log" 