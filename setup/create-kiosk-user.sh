#!/bin/bash

# Create Minimal Permission Kiosk User
# This user will have ONLY dashboard viewing permissions

set -e

echo "🐢 Creating Minimal Permission Kiosk User"
echo "=========================================="

# Check Home Assistant is running
if ! curl -s http://localhost:8123 > /dev/null; then
    echo "❌ Home Assistant is not running"
    exit 1
fi

echo "✅ Home Assistant is running"

# Create kiosk user configuration
echo "👤 Creating kiosk user configuration..."

# Create the kiosk user configuration file
cat > /home/shrimp/turtle-monitor/security/config/kiosk-user.yaml << 'EOF'
# Turtle Kiosk User Configuration
# This user has minimal permissions - ONLY dashboard viewing

# User details
name: "Turtle Kiosk"
username: "turtle_kiosk"
password: "turtle_kiosk_secure_2024!"

# Permissions - READ ONLY
permissions:
  # Dashboard access
  - "lovelace.read"
  - "lovelace-kiosk.read"
  
  # Sensor data (read only)
  - "sensor.read"
  - "binary_sensor.read"
  - "climate.read"
  - "light.read"
  - "switch.read"
  
  # Historical data (read only)
  - "history.read"
  - "logbook.read"
  
  # System status (read only)
  - "system_health.read"
  - "config.core.read"
  
  # NO WRITE PERMISSIONS
  # NO ADMIN PERMISSIONS
  # NO USER MANAGEMENT
  # NO CONFIGURATION ACCESS
  # NO AUTOMATION CONTROL
  # NO SCRIPT EXECUTION

# Dashboard restrictions
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
    - "127.0.0.1/32"  # Localhost only
    - "10.0.20.69/32" # Kiosk device IP only

# Session settings
session_timeout: 86400  # 24 hours
auto_logout: true
EOF

echo "✅ Kiosk user configuration created"

# Create the user creation script
cat > /home/shrimp/turtle-monitor/security/config/create-kiosk-user.py << 'EOF'
#!/usr/bin/env python3
"""
Create minimal permission kiosk user in Home Assistant
"""

import requests
import json
import sys
import time

def create_kiosk_user():
    """Create the turtle kiosk user with minimal permissions"""
    
    # Home Assistant API endpoint
    base_url = "http://localhost:8123"
    
    # First, we need to authenticate as admin
    print("🔐 Authenticating as admin...")
    
    # Try to get admin token from environment or prompt
    admin_token = None
    
    # Check if we have an admin token
    try:
        with open("/home/shrimp/turtle-monitor/.env", "r") as f:
            for line in f:
                if line.startswith("ADMIN_TOKEN="):
                    admin_token = line.split("=", 1)[1].strip()
                    break
    except:
        pass
    
    if not admin_token:
        print("❌ No admin token found")
        print("   Please create an admin token first:")
        print("   1. Go to http://localhost:8123")
        print("   2. Profile → Long-lived access tokens")
        print("   3. Create token named 'Admin Token'")
        print("   4. Add to .env file: ADMIN_TOKEN=your_token")
        return False
    
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    # Create the kiosk user
    print("👤 Creating turtle_kiosk user...")
    
    user_data = {
        "name": "Turtle Kiosk",
        "username": "turtle_kiosk",
        "password": "turtle_kiosk_secure_2024!",
        "group_ids": ["system-readonly"]  # Minimal permissions group
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/users",
            headers=headers,
            json=user_data
        )
        
        if response.status_code == 200:
            print("✅ Kiosk user created successfully")
            return True
        else:
            print(f"❌ Failed to create user: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

if __name__ == "__main__":
    if create_kiosk_user():
        print("🎉 Kiosk user setup complete!")
        print("   Username: turtle_kiosk")
        print("   Password: turtle_kiosk_secure_2024!")
        print("   Permissions: Dashboard viewing only")
    else:
        print("❌ Failed to create kiosk user")
        sys.exit(1)
EOF

chmod +x /home/shrimp/turtle-monitor/security/config/create-kiosk-user.py

echo "✅ User creation script prepared"

# Create network security configuration
echo "🌐 Creating network security configuration..."

cat > /home/shrimp/turtle-monitor/security/config/network-security.yaml << 'EOF'
# Network Security Configuration for Turtle Kiosk
# Restricts kiosk device to minimal network access

# Trusted networks (kiosk device only)
trusted_networks:
  - "127.0.0.1/32"      # Localhost
  - "10.0.20.69/32"     # Kiosk device IP (adjust as needed)

# Firewall rules for kiosk device
firewall_rules:
  kiosk_device:
    source: "10.0.20.69/32"
    destination: "localhost:8123"
    protocol: "tcp"
    action: "allow"
    description: "Kiosk to Home Assistant access"

# Network monitoring
network_monitoring:
  enabled: true
  log_file: "/home/shrimp/turtle-monitor/security/logs/network.log"
  alert_on_suspicious: true
  
# Access logging
access_logging:
  enabled: true
  log_file: "/home/shrimp/turtle-monitor/security/logs/kiosk-access.log"
  log_level: "INFO"
EOF

echo "✅ Network security configuration created"

echo ""
echo "🐢 Kiosk User Setup Complete!"
echo "=============================="
echo ""
echo "Next steps:"
echo "1. Create admin token: ./setup/create-admin-token.sh"
echo "2. Create kiosk user: python3 security/config/create-kiosk-user.py"
echo "3. Configure network security: ./setup/configure-network-security.sh"
echo "4. Test kiosk access: ./setup/test-kiosk-access.sh"
echo ""
echo "🔒 Security Note: The kiosk user has minimal permissions"
echo "   - Dashboard viewing only"
echo "   - No equipment control"
echo "   - No configuration access"
echo "   - No user management" 