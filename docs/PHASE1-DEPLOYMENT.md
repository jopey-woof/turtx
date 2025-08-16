# Phase 1 Deployment Guide - Turtle Monitoring System

**🐢 Phase 1: Basic Kiosk + Home Assistant Foundation**

This guide covers the deployment and validation of Phase 1 components only. **DO NOT proceed to Phase 2 until Phase 1 is 100% validated and working.**

## Prerequisites

- Ubuntu Server 22.04 LTS running on Beelink Mini PC
- SSH access to `shrimp@10.0.20.69`
- Git repository cloned to `/home/shrimp/turtle-monitor/`

## 🚀 Quick Start Deployment

### Step 1: Clone Repository

```bash
# SSH to the remote machine
ssh shrimp@10.0.20.69

# Clone the repository
cd /home/shrimp
git clone https://github.com/YOUR_USERNAME/turtle-monitor.git
cd turtle-monitor
```

### Step 2: Set Up Secrets

```bash
# Run the interactive secrets setup
./setup/setup-secrets.sh
```

**You will be prompted for:**
- Home Assistant admin username and password
- WiFi network credentials
- Email notification settings (Gmail app password required)
- Mobile webhook ID (can be left blank for now)
- Timezone setting (defaults to America/Los_Angeles)
- Location coordinates (defaults to Tigard, Oregon)

### Step 3: Run Bootstrap Setup

```bash
# Make scripts executable
chmod +x setup/*.sh
chmod +x kiosk/*.sh

# Run the main setup
./setup/bootstrap.sh
```

This script will:
- Install Docker and Docker Compose
- Install X11 and minimal desktop environment
- Install Chromium browser
- Set up touchscreen drivers
- Start Home Assistant container
- Configure kiosk mode service

## ✅ Phase 1 Validation Checklist

**CRITICAL: Each step must pass before proceeding to the next**

### 1. Verify Docker Installation
```bash
docker --version
docker-compose --version
docker ps
```
**Expected**: Docker running, no errors

### 2. Verify Home Assistant Container
```bash
cd docker
docker-compose logs homeassistant
curl http://localhost:8123
```
**Expected**: Home Assistant accessible at http://localhost:8123

### 3. Test X11 Display System
```bash
# Test X11 (run from local terminal with X forwarding)
ssh -X shrimp@10.0.20.69
export DISPLAY=:0
startx /usr/bin/openbox-session &
```
**Expected**: Desktop environment starts without errors

### 4. Test Chromium Browser
```bash
# On the remote machine
export DISPLAY=:0
chromium-browser --version
chromium-browser http://localhost:8123 &
```
**Expected**: Chromium opens and displays Home Assistant

### 5. Test Kiosk Service
```bash
# Start kiosk service
sudo systemctl start kiosk.service

# Check status
sudo systemctl status kiosk.service

# View logs
sudo journalctl -u kiosk.service -f
```
**Expected**: Service starts successfully, no errors

### 6. Validate Touchscreen (if connected)
- Physical test: Touch the screen
- Verify touch input responds in browser
- Test scrolling and button presses

### 7. Test Home Assistant Interface
Navigate to Home Assistant and verify:
- [ ] Login page appears
- [ ] Can log in with admin credentials
- [ ] Dashboard loads with turtle theme
- [ ] All placeholder sensors show data
- [ ] System controls work (toggle system armed, etc.)
- [ ] Scripts execute without errors
- [ ] Notifications appear when running health check

### 8. Test Notifications
```bash
# Test email notifications in Home Assistant
# Go to Developer Tools > Services
# Call: notify.turtle_email
# Message: "Test notification"
```
**Expected**: Email received successfully

### 9. Test Auto-Start Behavior
```bash
# Reboot system and verify auto-start
sudo reboot

# Wait for boot, then check services
ssh shrimp@10.0.20.69
sudo systemctl status kiosk.service
docker ps
```
**Expected**: Kiosk starts automatically, shows Home Assistant

## 🔧 Troubleshooting Phase 1

### Docker Issues
```bash
# Restart Docker service
sudo systemctl restart docker

# Check Docker logs
sudo journalctl -u docker.service

# Rebuild containers
cd docker
docker-compose down
docker-compose pull
docker-compose up -d
```

### X11/Display Issues
```bash
# Check X11 processes
ps aux | grep -E "(Xorg|xinit|chromium)"

# Restart X11
sudo systemctl restart kiosk.service

# Check display configuration
xrandr
```

### Home Assistant Issues
```bash
# Check HA logs
cd docker
docker-compose logs homeassistant -f

# Restart HA container
docker-compose restart homeassistant

# Check HA configuration
docker-compose exec homeassistant hass --script check_config
```

### Touchscreen Issues
```bash
# List input devices
xinput list

# Check touchscreen configuration
xinput list-props "DEVICE_NAME"

# Recalibrate touchscreen
xinput_calibrator
```

## 📊 Phase 1 Success Metrics

**Before proceeding to Phase 2, confirm:**

✅ **System Boot**: Automatic kiosk display after reboot (< 2 minutes)  
✅ **Home Assistant**: Accessible and stable (no crashes for 24 hours)  
✅ **User Interface**: All controls work via touchscreen  
✅ **Notifications**: Email alerts working  
✅ **System Health**: All system sensors showing data  
✅ **Recovery**: Services restart automatically after manual kill  
✅ **Stability**: System runs continuously for 48 hours without intervention  

## 🚫 What NOT to Do in Phase 1

- **DO NOT** connect any USB hardware yet (temperature sensors, cameras, etc.)
- **DO NOT** configure Zigbee devices
- **DO NOT** set up complex automations
- **DO NOT** proceed to Phase 2 until every validation step passes
- **DO NOT** ignore any error messages or warning signs

## ⏭️ Ready for Phase 2?

**Only proceed to Phase 2 if:**
1. ✅ All validation steps above pass
2. ✅ System has run stable for 48+ hours
3. ✅ You can reboot and everything starts automatically
4. ✅ All basic Home Assistant functions work perfectly
5. ✅ No persistent error messages in logs

**If any step fails:** Stop and troubleshoot before proceeding. A solid foundation is critical for the life-critical Phase 2 hardware integration.

---

## 📞 Support Information

**If you encounter issues:**
1. Check logs first: `sudo journalctl -u kiosk.service -f`
2. Verify .env file has correct values
3. Ensure all secrets are properly configured
4. Test individual components in isolation
5. Refer to troubleshooting section above

**Remember**: Phase 1 is the foundation. Take time to get it perfect before adding complexity.