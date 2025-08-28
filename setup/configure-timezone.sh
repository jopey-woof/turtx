#!/bin/bash

# Turtle Monitor - Timezone Configuration Script
# Sets system to Pacific time with automatic daylight savings adjustments

echo "🐢 Configuring Turtle Monitor System Timezone..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    echo "Run: sudo ./configure-timezone.sh"
    exit 1
fi

# Set timezone to Pacific time (Los Angeles)
echo "🕐 Setting timezone to America/Los_Angeles..."
timedatectl set-timezone America/Los_Angeles

# Verify the change
echo "✅ Timezone configured:"
timedatectl status

# Create daylight savings notification script
echo "📅 Creating daylight savings notification system..."
cat > /usr/local/bin/daylight-savings-notify.sh << 'EOF'
#!/bin/bash

# Daylight Savings Notification Script
# Runs twice a year to notify about time changes

CURRENT_DATE=$(date +%Y-%m-%d)
YEAR=$(date +%Y)

# Spring forward (second Sunday in March)
SPRING_FORWARD_2024="2024-03-10"
SPRING_FORWARD_2025="2025-03-09"
SPRING_FORWARD_2026="2026-03-08"

# Fall back (first Sunday in November)
FALL_BACK_2024="2024-11-03"
FALL_BACK_2025="2025-11-02"
FALL_BACK_2026="2026-11-01"

# Check if today is a daylight savings change day
if [ "$CURRENT_DATE" = "$SPRING_FORWARD_2024" ] || [ "$CURRENT_DATE" = "$SPRING_FORWARD_2025" ] || [ "$CURRENT_DATE" = "$SPRING_FORWARD_2026" ]; then
    echo "🕐 SPRING FORWARD: Clocks moved ahead 1 hour at 2:00 AM"
    echo "🐢 Turtle Monitor System: Time adjusted automatically"
    
    # Log the change
    logger "Turtle Monitor: Daylight Savings - Spring Forward applied"
    
    # Create a notification file for the dashboard
    echo "SPRING FORWARD - Clocks moved ahead 1 hour at 2:00 AM" > /tmp/daylight_savings_notification.txt
    echo "$(date)" >> /tmp/daylight_savings_notification.txt
    
elif [ "$CURRENT_DATE" = "$FALL_BACK_2024" ] || [ "$CURRENT_DATE" = "$FALL_BACK_2025" ] || [ "$CURRENT_DATE" = "$FALL_BACK_2026" ]; then
    echo "🕐 FALL BACK: Clocks moved back 1 hour at 2:00 AM"
    echo "🐢 Turtle Monitor System: Time adjusted automatically"
    
    # Log the change
    logger "Turtle Monitor: Daylight Savings - Fall Back applied"
    
    # Create a notification file for the dashboard
    echo "FALL BACK - Clocks moved back 1 hour at 2:00 AM" > /tmp/daylight_savings_notification.txt
    echo "$(date)" >> /tmp/daylight_savings_notification.txt
fi

# Clean up old notification files (older than 7 days)
find /tmp -name "daylight_savings_notification.txt" -mtime +7 -delete 2>/dev/null
EOF

# Make the notification script executable
chmod +x /usr/local/bin/daylight-savings-notify.sh

# Add to crontab to run daily at 3:00 AM (after any time changes)
echo "📅 Adding daily check to crontab..."
(crontab -l 2>/dev/null; echo "0 3 * * * /usr/local/bin/daylight-savings-notify.sh") | crontab -

# Create a systemd service for timezone monitoring
echo "🔧 Creating timezone monitoring service..."
cat > /etc/systemd/system/turtle-timezone-monitor.service << 'EOF'
[Unit]
Description=Turtle Monitor Timezone Monitor
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/daylight-savings-notify.sh
User=root

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
systemctl enable turtle-timezone-monitor.service

# Create a timezone info file for the dashboard
echo "📊 Creating timezone info for dashboard..."
cat > /home/shrimp/turtx/turtle-monitor/api/timezone_info.json << EOF
{
    "timezone": "America/Los_Angeles",
    "description": "Pacific Time (PT)",
    "utc_offset": "-08:00 (PST) / -07:00 (PDT)",
    "daylight_savings": "Automatic",
    "next_spring_forward": "2025-03-09",
    "next_fall_back": "2025-11-02",
    "configured_at": "$(date -Iseconds)",
    "system_time": "$(date)"
}
EOF

# Set proper permissions
chown shrimp:shrimp /home/shrimp/turtx/turtle-monitor/api/timezone_info.json

echo ""
echo "✅ Timezone Configuration Complete!"
echo ""
echo "🕐 Current System Time: $(date)"
echo "🌍 Timezone: $(timedatectl show --property=Timezone --value)"
echo "📅 Next Daylight Savings Changes:"
echo "   Spring Forward: March 9, 2025 (2:00 AM → 3:00 AM)"
echo "   Fall Back: November 2, 2025 (2:00 AM → 1:00 AM)"
echo ""
echo "🔔 Notifications will be sent automatically when time changes occur."
echo "📊 Dashboard will show timezone information and any recent changes."
echo ""
echo "🐢 Turtle Monitor System is now configured for Pacific Time!" 