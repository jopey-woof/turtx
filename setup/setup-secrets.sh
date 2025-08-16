#!/bin/bash

# Turtle Monitoring System - Interactive Secrets Setup
# This script prompts for all required secrets and creates secure configuration files
# Run this on the remote machine: ssh shrimp@10.0.20.69 './turtle-monitor/setup/setup-secrets.sh'

set -e

echo "🐢 Turtle Monitoring System - Secrets Setup"
echo "============================================="
echo ""
echo "This script will prompt you for all required secrets and create secure configuration files."
echo "Your input will be saved securely and NEVER committed to GitHub."
echo ""

# Create the .env file
ENV_FILE=".env"
SECRETS_DIR="secrets"

# Create directories
mkdir -p "$SECRETS_DIR"

echo "📝 Setting up environment variables..."

# Function to prompt for secret input
prompt_secret() {
    local var_name="$1"
    local prompt_text="$2"
    local is_password="$3"
    
    echo ""
    if [ "$is_password" = "true" ]; then
        echo -n "$prompt_text: "
        read -s value
        echo ""  # New line after hidden input
    else
        echo -n "$prompt_text: "
        read value
    fi
    
    # Add to .env file
    echo "${var_name}=${value}" >> "$ENV_FILE"
}

# Function to generate random secret
generate_secret() {
    openssl rand -hex 32
}

# Start creating .env file
echo "# Turtle Monitoring System Environment Variables" > "$ENV_FILE"
echo "# Generated on $(date)" >> "$ENV_FILE"
echo "# DO NOT COMMIT THIS FILE TO VERSION CONTROL" >> "$ENV_FILE"
echo "" >> "$ENV_FILE"

echo "🏠 HOME ASSISTANT CONFIGURATION"
echo "==============================="

prompt_secret "HA_ADMIN_USERNAME" "Home Assistant admin username (default: admin)" false
prompt_secret "HA_ADMIN_PASSWORD" "Home Assistant admin password (create a strong password)" true

# Generate random secret key
echo "HA_SECRET_KEY=$(generate_secret)" >> "$ENV_FILE"

echo ""
echo "🌐 NETWORK CONFIGURATION"
echo "========================"

prompt_secret "WIFI_SSID" "WiFi network name (SSID)" false
prompt_secret "WIFI_PASSWORD" "WiFi password" true

# Set default network values
echo "HA_TRUSTED_NETWORKS=10.0.20.0/24,172.17.0.0/16" >> "$ENV_FILE"
echo "HA_EXTERNAL_URL=http://10.0.20.69:8123" >> "$ENV_FILE"
echo "HA_INTERNAL_URL=http://localhost:8123" >> "$ENV_FILE"
echo "REMOTE_HOST=10.0.20.69" >> "$ENV_FILE"
echo "REMOTE_USER=shrimp" >> "$ENV_FILE"
echo "REMOTE_BASE_PATH=/home/shrimp/turtle-monitor" >> "$ENV_FILE"

echo ""
echo "📧 EMAIL NOTIFICATIONS"
echo "======================"
echo "For Gmail, you'll need to create an App Password:"
echo "1. Go to Google Account settings"
echo "2. Security > 2-Step Verification > App passwords"
echo "3. Generate an app password for 'Mail'"
echo ""

prompt_secret "EMAIL_USERNAME" "Email address for notifications" false
prompt_secret "EMAIL_PASSWORD" "Email app password (NOT your regular password)" true
prompt_secret "EMAIL_RECIPIENT" "Email address to receive alerts (can be same as above)" false

# Default email settings
echo "EMAIL_SMTP_HOST=smtp.gmail.com" >> "$ENV_FILE"
echo "EMAIL_SMTP_PORT=587" >> "$ENV_FILE"

echo ""
echo "📱 MOBILE NOTIFICATIONS"
echo "======================="
echo "This can be configured later in Home Assistant mobile app"

prompt_secret "HA_MOBILE_WEBHOOK_ID" "Mobile webhook ID (leave blank for now, configure later)" false

echo ""
echo "🕐 TIMEZONE & LOCATION"
echo "====================="

# Set timezone with default
echo -n "Your timezone [America/Los_Angeles]: "
read tz_input
if [ -z "$tz_input" ]; then
    echo "TZ=America/Los_Angeles" >> "$ENV_FILE"
else
    echo "TZ=$tz_input" >> "$ENV_FILE"
fi

# Set location coordinates with Tigard, Oregon defaults
echo -n "Home latitude [45.4312]: "
read lat_input
if [ -z "$lat_input" ]; then
    echo "HOME_LATITUDE=45.4312" >> "$ENV_FILE"
else
    echo "HOME_LATITUDE=$lat_input" >> "$ENV_FILE"
fi

echo -n "Home longitude [-122.7715]: "
read lon_input  
if [ -z "$lon_input" ]; then
    echo "HOME_LONGITUDE=-122.7715" >> "$ENV_FILE"
else
    echo "HOME_LONGITUDE=$lon_input" >> "$ENV_FILE"
fi

echo -n "Home elevation in meters [46]: "
read elev_input
if [ -z "$elev_input" ]; then
    echo "HOME_ELEVATION=46" >> "$ENV_FILE"
else
    echo "HOME_ELEVATION=$elev_input" >> "$ENV_FILE"
fi

echo ""
echo "🔧 HARDWARE DEFAULTS"
echo "===================="

# Set hardware defaults
echo "CAMERA_DEVICE=/dev/video0" >> "$ENV_FILE"
echo "CAMERA_RESOLUTION=1920x1080" >> "$ENV_FILE"
echo "CAMERA_FPS=30" >> "$ENV_FILE"
echo "TEMP_SENSOR_DEVICE=/dev/ttyUSB0" >> "$ENV_FILE"
echo "DISPLAY_RESOLUTION=1024x600" >> "$ENV_FILE"
echo 'CHROMIUM_FLAGS="--kiosk --disable-features=VizDisplayCompositor --disable-backgrounding-occluded-windows"' >> "$ENV_FILE"

# Create Home Assistant secrets.yaml file
echo ""
echo "📝 Creating Home Assistant secrets.yaml..."

# Source the environment variables we just created
set -a
source "$ENV_FILE"
set +a

# Create the secrets.yaml file with actual values
cat > homeassistant/secrets.yaml << EOF
# Turtle Monitoring System - Home Assistant Secrets
# Generated on $(date)
# DO NOT COMMIT THIS FILE TO VERSION CONTROL

# Location
home_latitude: $HOME_LATITUDE
home_longitude: $HOME_LONGITUDE
home_elevation: $HOME_ELEVATION

# Timezone  
timezone: $TZ

# Database URL (SQLite by default)
database_url: sqlite:////config/home-assistant_v2.db

# Email notifications
email_smtp_host: $EMAIL_SMTP_HOST
email_smtp_port: $EMAIL_SMTP_PORT
email_username: $EMAIL_USERNAME
email_password: $EMAIL_PASSWORD
email_recipient: $EMAIL_RECIPIENT

# Home Assistant URLs
external_url: $HA_EXTERNAL_URL
internal_url: $HA_INTERNAL_URL

# API tokens (generated in HA UI)
mobile_webhook_id: $HA_MOBILE_WEBHOOK_ID

# Additional secrets as needed
http_password: $HA_HTTP_PASSWORD
EOF

# Set secure file permissions
chmod 600 "$ENV_FILE"
chmod 600 "homeassistant/secrets.yaml"
chmod 700 "$SECRETS_DIR"

echo ""
echo "✅ Secrets setup complete!"
echo ""
echo "Files created:"
echo "- .env (secure environment variables)"
echo "- homeassistant/secrets.yaml (Home Assistant secrets with your real values)"
echo "- secrets/ directory (for additional secret files)"
echo ""
echo "🔒 Security notes:"
echo "- .env file permissions set to 600 (owner read/write only)"
echo "- secrets.yaml file permissions set to 600 (owner read/write only)"
echo "- secrets/ directory permissions set to 700 (owner access only)"
echo "- These files are already excluded from Git via .gitignore"
echo ""
echo "Next step: Run ./setup/bootstrap.sh to set up the system"
echo ""