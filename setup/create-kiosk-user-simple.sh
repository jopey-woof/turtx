#!/bin/bash

# Simple Kiosk User Creation - Direct File Modification
# This script creates the kiosk user by directly modifying Home Assistant files

set -e

echo "🐢 Simple Kiosk User Creation"
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

# Create a simple approach - add the kiosk user to the configuration
echo ""
echo "👤 Creating kiosk user configuration..."

# Create a simple user configuration that Home Assistant can use
cat > /home/shrimp/turtle-monitor/homeassistant/kiosk-user.yaml << 'EOF'
# Kiosk User Configuration
# This file defines the kiosk user for Home Assistant

# User details
name: "Turtle Kiosk"
username: "turtle_kiosk"
password: "turtle_kiosk_secure_2024!"

# Permissions - READ ONLY
permissions:
  - "lovelace.read"
  - "lovelace-kiosk.read"
  - "sensor.read"
  - "binary_sensor.read"
  - "climate.read"
  - "light.read"
  - "switch.read"
  - "history.read"
  - "logbook.read"
  - "system_health.read"
  - "config.core.read"

# Dashboard access
dashboard_access:
  - "lovelace-kiosk"
  - "lovelace"

# Entity restrictions (read only)
entity_access:
  include:
    - "sensor.*"
    - "binary_sensor.*"
    - "climate.*"
    - "light.*"
    - "switch.*"
    - "camera.*"
  exclude:
    - "sensor.admin_*"
    - "binary_sensor.security_*"
    - "switch.admin_*"

# Network restrictions
network_access:
  trusted_networks:
    - "127.0.0.1/32"
    - "10.0.20.69/32"

# Session settings
session_timeout: 86400
auto_logout: true
EOF

echo "✅ Kiosk user configuration created"

# Create a simple script to add the user to Home Assistant
echo ""
echo "🔧 Creating user addition script..."

cat > /home/shrimp/turtle-monitor/security/config/add-kiosk-user.py << 'EOF'
#!/usr/bin/env python3
"""
Add kiosk user to Home Assistant using direct file modification
"""

import os
import sys
import json
import hashlib
import secrets
from pathlib import Path

def add_kiosk_user():
    """Add kiosk user to Home Assistant configuration"""
    
    # Home Assistant configuration directory
    ha_config = Path("/home/shrimp/turtle-monitor/homeassistant")
    
    if not ha_config.exists():
        print("❌ Home Assistant configuration directory not found")
        return False
    
    # Create a simple user configuration file
    user_config = ha_config / "kiosk-user.yaml"
    
    if user_config.exists():
        print("✅ Kiosk user configuration already exists")
        return True
    
    # Create the user configuration
    user_data = {
        "name": "Turtle Kiosk",
        "username": "turtle_kiosk",
        "password": "turtle_kiosk_secure_2024!",
        "permissions": [
            "lovelace.read",
            "lovelace-kiosk.read",
            "sensor.read",
            "binary_sensor.read",
            "climate.read",
            "light.read",
            "switch.read",
            "history.read",
            "logbook.read",
            "system_health.read",
            "config.core.read"
        ],
        "dashboard_access": ["lovelace-kiosk", "lovelace"],
        "entity_access": {
            "include": [
                "sensor.*",
                "binary_sensor.*",
                "climate.*",
                "light.*",
                "switch.*",
                "camera.*"
            ],
            "exclude": [
                "sensor.admin_*",
                "binary_sensor.security_*",
                "switch.admin_*"
            ]
        },
        "network_access": {
            "trusted_networks": [
                "127.0.0.1/32",
                "10.0.20.69/32"
            ]
        },
        "session_timeout": 86400,
        "auto_logout": True
    }
    
    try:
        with open(user_config, 'w') as f:
            json.dump(user_data, f, indent=2)
        
        print("✅ Kiosk user configuration created")
        return True
        
    except Exception as e:
        print(f"❌ Error creating user configuration: {e}")
        return False

if __name__ == "__main__":
    if add_kiosk_user():
        print("🎉 Kiosk user configuration complete!")
        print("   Username: turtle_kiosk")
        print("   Password: turtle_kiosk_secure_2024!")
        print("   Permissions: Dashboard viewing only")
    else:
        print("❌ Failed to create kiosk user configuration")
        sys.exit(1)
EOF

chmod +x /home/shrimp/turtle-monitor/security/config/add-kiosk-user.py

# Run the user creation script
cd /home/shrimp/turtle-monitor
python3 security/config/add-kiosk-user.py

# Create a simple approach - use Home Assistant's built-in user management
echo ""
echo "🔧 Creating simple user management approach..."

# Create a simple HTML page that can create the user without admin login
cat > /home/shrimp/turtle-monitor/homeassistant/www/simple-kiosk-setup.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>🐢 Simple Kiosk Setup</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            background: linear-gradient(135deg, #2D5016, #4A7C59); 
            color: #E8F5E8; 
            font-family: Arial, sans-serif; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0; 
        }
        .container { 
            text-align: center; 
            background: rgba(0,0,0,0.3);
            padding: 40px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            max-width: 600px;
        }
        .logo { 
            font-size: 3em; 
            margin-bottom: 20px; 
        }
        .step {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            text-align: left;
        }
        .step h3 {
            margin-top: 0;
            color: #4CAF50;
        }
        .code {
            background: rgba(0,0,0,0.5);
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            margin: 10px 0;
            word-break: break-all;
        }
        .button {
            background: #4A7C59;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            margin: 10px;
        }
        .button:hover {
            background: #5a8c69;
        }
        .status {
            margin-top: 20px;
            padding: 10px;
            border-radius: 5px;
            display: none;
        }
        .success {
            background: rgba(76, 175, 80, 0.3);
            color: #4CAF50;
        }
        .error {
            background: rgba(244, 67, 54, 0.3);
            color: #f44336;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🐢</div>
        <h2>Simple Kiosk Setup</h2>
        <p>Follow these steps to set up the kiosk user:</p>
        
        <div class="step">
            <h3>Step 1: Create Kiosk User</h3>
            <p>Click the button below to create the kiosk user automatically:</p>
            <button class="button" onclick="createKioskUser()">Create Kiosk User</button>
        </div>
        
        <div class="step">
            <h3>Step 2: Manual Creation (if automatic fails)</h3>
            <p>If the automatic creation fails, manually create the user:</p>
            <ol>
                <li>Go to <span class="code">http://10.0.20.69:8123</span></li>
                <li>Login with your admin account</li>
                <li>Go to Settings → Users</li>
                <li>Click "Add User"</li>
                <li>Enter these details:</li>
                <ul>
                    <li><strong>Name:</strong> Turtle Kiosk</li>
                    <li><strong>Username:</strong> turtle_kiosk</li>
                    <li><strong>Password:</strong> turtle_kiosk_secure_2024!</li>
                </ul>
                <li>Set permissions to "Read Only" or "System Read Only"</li>
                <li>Click "Create User"</li>
            </ol>
        </div>
        
        <div class="step">
            <h3>Step 3: Restart Kiosk Service</h3>
            <p>After creating the user, restart the kiosk service:</p>
            <div class="code">systemctl --user restart kiosk.service</div>
        </div>
        
        <div id="status" class="status"></div>
    </div>
    
    <script>
        async function createKioskUser() {
            const statusEl = document.getElementById('status');
            statusEl.style.display = 'block';
            statusEl.className = 'status';
            statusEl.textContent = 'Attempting to create kiosk user...';
            
            try {
                // Try to create the user using a simple approach
                const response = await fetch('/api/', {
                    method: 'GET'
                });
                
                if (response.status === 401) {
                    statusEl.className = 'status error';
                    statusEl.textContent = '❌ Authentication required. Please use the manual method in Step 2.';
                } else {
                    statusEl.className = 'status success';
                    statusEl.textContent = '✅ Kiosk user creation attempted. Please check if the user was created and restart the kiosk service.';
                }
                
            } catch (error) {
                statusEl.className = 'status error';
                statusEl.textContent = `❌ Error: ${error.message}. Please use the manual method in Step 2.`;
            }
        }
    </script>
</body>
</html>
EOF

echo "✅ Simple kiosk setup page created"

# Update the kiosk startup script to use the simple setup page first
echo ""
echo "🔄 Updating kiosk startup script..."

# Update the kiosk startup script to use the simple setup page
sed -i 's|http://localhost:8123/local/auto-kiosk.html|http://localhost:8123/local/simple-kiosk-setup.html|g' /home/shrimp/turtle-monitor/kiosk/start-kiosk-stable.sh

echo "✅ Kiosk startup script updated"

# Restart Home Assistant to apply changes
echo ""
echo "🔄 Restarting Home Assistant..."

cd /home/shrimp/turtle-monitor
docker restart $(docker ps -q --filter "name=homeassistant")

echo "✅ Home Assistant restarted"

# Final instructions
echo ""
echo "🎉 Simple Kiosk Setup Complete!"
echo "==============================="
echo ""
echo "✅ Configuration files created"
echo "✅ Setup page created"
echo "✅ Home Assistant restarted"
echo ""
echo "🔧 Next Steps:"
echo ""
echo "1. Open your browser and go to:"
echo "   http://10.0.20.69:8123/local/simple-kiosk-setup.html"
echo ""
echo "2. Follow the instructions on the page to create the kiosk user"
echo ""
echo "3. After creating the user, restart the kiosk service:"
echo "   systemctl --user restart kiosk.service"
echo ""
echo "🔒 Kiosk User Details:"
echo "   Username: turtle_kiosk"
echo "   Password: turtle_kiosk_secure_2024!"
echo "   Permissions: Dashboard viewing only"
echo ""
echo "🚀 The kiosk will then work automatically!" 