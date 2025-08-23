# 🐢 Secure Kiosk Setup Guide

## Complete Security-First Kiosk Solution

This guide implements a comprehensive, security-first solution for the Home Assistant kiosk login issue. The solution provides seamless kiosk access while maintaining maximum security for the turtle habitat monitoring system.

## 🔒 Security Approach

**Method: Minimal Permission Kiosk User (RECOMMENDED)**
- Creates dedicated kiosk user with ONLY dashboard viewing permissions
- NO administrative access, NO device control permissions
- NO access to configuration, settings, or other users
- ONLY read access to turtle sensors and dashboard
- Automatic login for this restricted user
- All kiosk activities logged for monitoring

## 📋 Prerequisites

- Home Assistant running on Ubuntu Server
- Docker and docker-compose installed
- Kiosk device (tablet/display) connected to the same network
- Admin access to Home Assistant

## 🚀 Quick Setup (Step-by-Step)

### Step 1: Create Admin Token

1. **Open your browser** and go to: `http://10.0.20.69:8123`
2. **Log in** with your admin account
3. **Go to Profile** (click your username in the sidebar)
4. **Scroll down** to "Long-lived access tokens"
5. **Click "CREATE TOKEN"**
6. **Name it**: "Turtle Kiosk Admin Token"
7. **Click "OK"**
8. **COPY THE TOKEN** (you won't see it again!)

### Step 2: Add Token to Environment

Run this command (replace `YOUR_TOKEN_HERE` with the actual token):

```bash
echo "ADMIN_TOKEN=YOUR_TOKEN_HERE" >> /home/shrimp/turtle-monitor/.env
```

### Step 3: Run the Deployment Script

```bash
cd /home/shrimp/turtle-monitor
./setup/deploy-secure-kiosk.sh
```

### Step 4: Test the Kiosk

```bash
systemctl --user restart kiosk.service
```

## 🔧 Manual Setup (Alternative)

If you prefer to set up manually or the automated script fails:

### 1. Create Security Infrastructure

```bash
cd /home/shrimp/turtle-monitor
mkdir -p security/{logs,config,monitoring}
mkdir -p kiosk/secure
chmod 700 security
```

### 2. Create Kiosk User

```bash
# Run the kiosk user creation script
./setup/create-kiosk-user.sh
```

### 3. Configure Home Assistant

Add this to your `homeassistant/configuration.yaml`:

```yaml
# Kiosk Security Configuration
http:
  trusted_networks:
    - 127.0.0.1/32
    - 10.0.20.69/32  # Kiosk device IP
  use_x_forwarded_for: true
  trusted_proxies:
    - 127.0.0.1
    - 10.0.20.69

# Security logging
logger:
  default: info
  logs:
    homeassistant.core: debug
    homeassistant.auth: debug
```

### 4. Restart Services

```bash
docker-compose restart homeassistant
systemctl --user restart kiosk.service
```

## 🧪 Testing the Setup

Run the test script to verify everything is working:

```bash
./setup/test-kiosk-access.sh
```

## 📊 Monitoring and Security

### View Kiosk Access Logs

```bash
tail -f /home/shrimp/turtle-monitor/security/logs/kiosk-access.log
```

### View Security Events

```bash
tail -f /home/shrimp/turtle-monitor/security/logs/security-events.log
```

### Check Kiosk Service Status

```bash
systemctl --user status kiosk.service
```

## 🔒 Security Features Implemented

### User Permissions
- **Kiosk User**: `turtle_kiosk` / `turtle_kiosk_secure_2024!`
- **Permissions**: Dashboard viewing only
- **NO**: Equipment control, configuration access, user management

### Network Security
- **Trusted Networks**: Only localhost and kiosk device IP
- **Firewall Rules**: Kiosk can only access Home Assistant
- **Access Logging**: All authentication attempts logged

### Browser Security
- **Kiosk Mode**: Full-screen, no navigation bar
- **Security Flags**: Disabled developer tools, right-click, etc.
- **URL Restrictions**: Locked to Home Assistant only

### Monitoring
- **Access Logging**: All kiosk activities logged
- **Security Events**: Suspicious activity detection
- **Network Monitoring**: Traffic analysis and alerting

## 🚨 Troubleshooting

### Kiosk Not Starting

```bash
# Check service status
systemctl --user status kiosk.service

# Check logs
journalctl --user -u kiosk.service -f

# Restart service
systemctl --user restart kiosk.service
```

### Login Issues

```bash
# Test kiosk user authentication
curl -X POST http://localhost:8123/auth/login_flow \
  -H "Content-Type: application/json" \
  -d '{"username": "turtle_kiosk", "password": "turtle_kiosk_secure_2024!", "client_id": "test"}'
```

### Network Issues

```bash
# Check Home Assistant accessibility
curl http://localhost:8123

# Check kiosk device IP
hostname -I
```

### Security Issues

```bash
# Check security logs
tail -f /home/shrimp/turtle-monitor/security/logs/security-events.log

# Verify user permissions
./setup/test-kiosk-access.sh
```

## 🔄 Maintenance

### Regular Security Checks

```bash
# Weekly security audit
./setup/test-kiosk-access.sh

# Check for unauthorized access
grep "unauthorized" /home/shrimp/turtle-monitor/security/logs/kiosk-access.log

# Verify user permissions haven't changed
curl -H "Authorization: Bearer KIOSK_TOKEN" http://localhost:8123/api/
```

### Token Management

- **Admin Token**: Consider revoking after kiosk setup
- **Kiosk Token**: Automatically managed by the system
- **Session Timeout**: 24 hours (configurable)

### Backup and Recovery

```bash
# Backup kiosk configuration
tar -czf kiosk-backup-$(date +%Y%m%d).tar.gz security/ kiosk/

# Restore from backup
tar -xzf kiosk-backup-YYYYMMDD.tar.gz
```

## 🎯 Success Criteria

The setup is successful when:

- ✅ Kiosk automatically shows turtle dashboard without login prompts
- ✅ Survives reboots, network changes, and system updates
- ✅ Dashboard appears within 10 seconds of device boot
- ✅ Automatic recovery from network or authentication issues
- ✅ Clear status messages (not technical errors) if issues occur
- ✅ Overall Home Assistant security is NOT compromised
- ✅ Kiosk cannot be used to gain unauthorized system access
- ✅ All kiosk activities are logged for security review

## 🔒 Security Notes

**Critical Success Factor**: The turtle owner gets seamless kiosk access WITHOUT compromising the security of their home automation system that controls life support equipment.

- **Life Support Context**: This system controls turtle habitat equipment (heating, lighting, potentially water systems)
- **Security Priority**: Cannot compromise overall Home Assistant security while solving kiosk access
- **Physical Security**: Kiosk is physically secure (next to turtle enclosure, controlled access)
- **Network Security**: Must maintain network isolation and access controls

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the security logs for any errors
3. Run the test script to identify specific issues
4. Ensure all prerequisites are met
5. Verify network connectivity and Home Assistant status

## 🎉 Completion

Once the setup is complete, your kiosk will:

- **Automatically login** to the turtle dashboard
- **Display sensor data** and habitat status
- **Provide read-only access** to monitoring information
- **Maintain security** of the overall system
- **Log all activities** for monitoring and audit

The turtle owner will have convenient, secure access to monitor their turtle's habitat without any login prompts or technical complications. 