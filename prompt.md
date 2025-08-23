# Eastern Box Turtle Enclosure Automation System

I am developing a turtle monitoring system that will be deployed on a remote machine. I'm using a **local development → GitHub → remote deployment** workflow.

## Development Workflow
- **Local Development**: I'm developing all configurations, automations, and code locally using Cursor AI
- **Version Control**: Push all changes to GitHub repository for version control
- **Remote Deployment**: Pull updates from GitHub to the remote turtle monitoring system
- **Target Machine**: Beelink Mini PC with Ubuntu Server + Docker + Home Assistant already running

## Remote Machine Current Status
- **✅ Ubuntu Server 22.04 LTS** - Installed and running on Beelink Mini PC
- **✅ Docker** - Installed and configured
- **✅ Home Assistant** - Running in Docker container
- **✅ GitHub Access** - Can pull repository updates
- **✅ TEMPerHUM Sensor Integration** - Complete production-ready integration with MQTT auto-discovery
- **✅ Secure Kiosk Implementation** - Zero-login kiosk access with security-first architecture
- **✅ Automated Deployment** - One-command deployment scripts for all components
- **Ready to deploy**: All configurations I develop locally will be pulled to this machine

## Hardware Setup (Remote Machine)
- **Host**: Beelink Mini PC (running Ubuntu Server 22.04 LTS)
- **Display**: ROADOM 10.1" Touchscreen Monitor (1024×600 IPS) - Primary kiosk interface
- **Connectivity**: 3-foot Anker HDMI cable for display connection
- **Sensors**: ✅ TEMPerHUM V4.1 USB temperature/humidity sensors (dual sensors - shell + enclosure)
- **Camera**: Arducam 1080P Day & Night Vision USB Camera
- **Zigbee Hub**: Sonoff Zigbee USB Dongle Plus (ZBDongle-E 3.0)
- **Smart Control**: ZigBee Smart Plugs 4-pack with energy monitoring (15A outlets, Zigbee repeaters)
- **USB Expansion**: Anker 4-Port USB 3.0 Hub + AINOPE USB 3.0 extension cables
- **Primary Heat Control**: Vivarium Electronics VE-200 w/night drop (existing, reliable thermostat)

## Project Goals - CURRENT STATUS
1. **✅ Touchscreen Kiosk Interface**: Complete secure kiosk implementation with zero-login access
2. **✅ Environmental Monitoring**: TEMPerHUM sensors fully integrated with MQTT auto-discovery
3. **🔄 Smart Cooling Control**: Zigbee smart plugs ready for integration (next phase)
4. **🔄 Live Camera Feed**: Arducam camera ready for integration (next phase)
5. **🔄 Energy Monitoring**: Smart plugs ready for energy monitoring (next phase)
6. **🔄 Push Notifications**: Mobile app and email alerts ready for implementation (next phase)
7. **✅ Data Integration**: TEMPerHUM sensors logging data alongside existing VE-200 heat controller
8. **🔄 Simple Device Control**: Touch controls ready for smart plug integration (next phase)
9. **🔄 Visual Alerts**: Alert system ready for implementation (next phase)
10. **✅ Beautiful Turtle Theming**: Custom turtle theme implemented in Home Assistant

## Specific Requirements - CURRENT STATUS
- **✅ Temperature range**: 70-85°F (21-29°C) with basking spot up to 90°F (32°C) - MONITORING ACTIVE
- **✅ Humidity range**: 60-80% for eastern box turtles - MONITORING ACTIVE
- **🔄 Day/night lighting cycles**: Ready for smart plug integration (next phase)
- **🔄 Critical Alert Scenarios**: Alert system ready for implementation (next phase)
- **🔄 Notification Preferences**: Tiered alerts ready for implementation (next phase)
- **🔄 Delivery Methods**: Mobile app and email ready for implementation (next phase)
- **✅ Historical data visualization**: TEMPerHUM data logging and visualization active
- **🔄 Equipment Failure Detection**: Ready for smart plug integration (next phase)

## Secrets Management & Security Requirements

**⚠️ CRITICAL: All secrets must be kept out of GitHub repository and version control**

### Instructions for AI Assistant:
**When working with this prompt, you MUST:**
1. **Follow the sequential development approach** - Focus on ONE phase at a time, validate before proceeding
2. **Build on existing foundation** - TEMPerHUM sensors and kiosk are complete, focus on next phases
3. **Prompt the user for actual secret values** needed for configurations (Wi-Fi passwords, email credentials, etc.)
4. **Use the real secrets** provided by the user to create working configuration files
5. **Create both working configs** (with real secrets) AND template versions (with placeholders)
6. **Clearly identify** which files contain real secrets and must be added to `.gitignore`
7. **Remind the user** to never commit files containing actual secrets to GitHub
8. **Insist on validation** - Don't provide Phase 2+ configurations until Phase 1 is confirmed working
9. **Keep configurations minimal** - Start simple, add complexity only after basics work perfectly
10. **Use current versions** - Always specify latest stable versions of containers, APIs, and software components

### Required Secrets for System Configuration:
- **Wi-Fi Credentials**: Network SSID and password for remote machine connectivity
- **Home Assistant Admin Account**: Username and strong password for HA admin user
- **Email Notification Credentials**: SMTP server details, username, and app-specific password
- **Mobile App Integration**: Home Assistant long-lived access tokens for mobile app
- **Zigbee Network Key**: Secure key for Zigbee mesh network (generated during setup)
- **Camera Access Credentials**: Any required authentication for USB camera access
- **SSL/TLS Certificates**: If enabling HTTPS access (recommended for security)
- **API Keys**: Any third-party service integrations (weather, external sensors, etc.)

### Security Implementation Requirements:
1. **Development Workflow**: AI assistant will prompt for real secrets to create working configs during development
2. **Dual File Creation**: Generate both working files (with real secrets) and template files (with placeholders)
3. **Environment Files**: Use `.env` files for secrets (add to `.gitignore`)
4. **Secure Storage**: Store secrets in `/home/turtle/secrets/` directory on remote machine
5. **File Permissions**: Restrict secret files to `600` permissions (owner read/write only)
6. **Repository Safety**: Clear identification of files that must never be committed to GitHub
7. **Documentation**: Provide clear instructions for administrators on secret management
8. **Backup Strategy**: Secure backup procedures for critical secrets and configurations

### Repository Structure for Secrets:
```
├── config/
│   ├── homeassistant/
│   │   ├── configuration.yaml (template with placeholders)
│   │   └── secrets.yaml.template (template file, NOT actual secrets)
├── deployment/
│   ├── setup-secrets.sh (script to create secrets interactively)
│   └── deploy-secure.sh (deployment script that sources secrets)
├── .env.template (example environment file)
└── .gitignore (MUST include all secret files and directories)
```

**🔒 Never commit to GitHub:**
- `.env` files
- `secrets.yaml`
- Any files containing passwords, tokens, or keys
- Private certificates or keys
- Personal network credentials

## Technical Tasks - CURRENT STATUS

### ✅ COMPLETED: Kiosk Display Setup
1. **✅ Install Display Components**: X11, lightweight desktop environment, and Chromium for kiosk mode
2. **✅ Touchscreen Configuration**: Touch input drivers and calibration for the 10.1" 1024×600 display
3. **✅ Auto-boot Kiosk**: Systemd services for automatic login and Chromium kiosk startup
4. **✅ Turtle Dashboard Auto-Launch**: System automatically displays custom turtle-themed Home Assistant dashboard
5. **✅ Multi-Layer Recovery System**: Comprehensive watchdog and recovery services implemented

### ✅ COMPLETED: Environmental Sensor Integration
6. **✅ Mission-Critical USB Device Management**: Bulletproof udev rules and permissions for TEMPerHUM sensors
7. **✅ Environmental Sensor Reliability**: TEMPerHUM V4.1 integration with 30-second max recovery, calibration validation
8. **✅ MQTT Auto-Discovery**: Complete Home Assistant integration with automatic entity creation
9. **✅ Production Service**: Systemd service with comprehensive logging and error recovery
10. **✅ Automated Deployment**: One-command deployment script with complete system setup

### 🔄 NEXT PHASE: Hardware Integration
11. **🔄 Zigbee Network Resilience**: Configure Sonoff dongle with mesh repair, coordinator backup, and automatic device re-pairing
12. **🔄 Climate Control Integration**: Smart plug configuration with 15-second max recovery, power state verification, and emergency manual override
13. **🔄 Camera Surveillance System**: Arducam integration with multi-layer recovery, stream redundancy, and 60-second maximum downtime

### 🔄 NEXT PHASE: Life-Critical Home Assistant Configuration
14. **✅ Skip Onboarding Setup**: Home Assistant configured to bypass initial onboarding wizard
15. **✅ Kiosk Mode Plugin**: Home Assistant 'Kiosk Mode' plugin configured for optimal touchscreen experience
16. **✅ Mission-Critical Device Integrations**: TEMPerHUM sensors fully integrated with health monitoring
17. **🔄 Life-Critical Environmental Automations**: Temperature/humidity monitoring with immediate alerts and emergency responses
18. **🔄 Equipment Failure Detection**: Comprehensive automations to detect ALL device failures via power consumption, connectivity, and health checks
19. **🔄 Emergency Climate Control**: Smart plug automations with failsafes, manual overrides, and coordination with VE-200 thermostat
20. **🔄 Environmental Cycles**: Day/night lighting and temperature variations with backup controls and failure handling

### 🔄 NEXT PHASE: Life-Critical Alerts & Emergency Notifications
21. **🔄 Multi-Channel Alert System**: Configure immediate notifications via mobile app, email, and on-screen alerts for ALL critical failures
22. **🔄 Emergency Contact Escalation**: Progressive alert escalation for life-threatening conditions (temperature extremes, complete system failures)
23. **🔄 Critical Alert Automations**: Immediate alerts for environmental dangers, equipment failures, and system outages with severity-based responses
24. **🔄 Emergency Interface**: Touch-friendly emergency controls and alert acknowledgment with manual override capabilities

### ✅ COMPLETED: Turtle-Themed Interface Design
25. **✅ Custom Turtle Dashboard**: Dedicated turtle-themed Home Assistant dashboard as the primary interface
26. **✅ Custom CSS Theme**: Turtle-inspired colors, fonts, and styling optimized for 1024×600 touchscreen
27. **✅ Custom Icons**: Turtle, leaf, water drop, and nature-themed icons throughout interface
28. **✅ Touch-Optimized Layout**: Large buttons and controls perfect for finger navigation
29. **✅ Dashboard Cards**: Beautiful cards for temperature, humidity, and device status
30. **✅ Animations**: Subtle nature-themed animations (water ripples, gentle movements)
31. **✅ Seasonal Themes**: Dynamic color schemes that change with day/night cycles

## ⚡ CRITICAL: Complete System Reliability & Recovery Requirements

**🐢 LIFE-CRITICAL SYSTEM: ALL components must have bulletproof reliability - a living creature depends on this**

**🎯 PRIMARY GOALS:**
- **✅ Display**: Maximum 30-second recovery time - IMPLEMENTED
- **🔄 Camera**: Maximum 60-second recovery time - NEXT PHASE
- **✅ Temperature Monitoring**: Maximum 30-second sensor recovery time - IMPLEMENTED
- **✅ Humidity Monitoring**: Maximum 30-second sensor recovery time - IMPLEMENTED
- **🔄 Smart Plug Control**: Maximum 15-second recovery time (heating/cooling critical) - NEXT PHASE
- **🔄 Zigbee Network**: Maximum 45-second recovery time - NEXT PHASE
- **✅ Home Assistant Core**: Maximum 60-second recovery time - IMPLEMENTED
- **🔄 All Environmental Controls**: Immediate failsafe activation during outages - NEXT PHASE

### Multi-Layer Recovery Architecture:
1. **✅ Browser-Level Recovery** (5-10 seconds): IMPLEMENTED
   - Chromium process monitoring with immediate restart on crash
   - Automatic page refresh every 5 minutes to prevent browser memory issues
   - JavaScript-based page health monitoring and auto-reload

2. **✅ X11/Display Recovery** (10-15 seconds): IMPLEMENTED
   - X server watchdog service to restart display manager on failure
   - Automatic graphics driver recovery and reinitialization
   - Display connection monitoring for touchscreen disconnect/reconnect

3. **✅ System-Level Recovery** (15-30 seconds): IMPLEMENTED
   - Systemd service dependencies with automatic restart policies
   - Desktop environment watchdog with rapid restart capability
   - Complete kiosk stack restart as last resort

4. **✅ Environmental Sensor Recovery** (10-30 seconds): IMPLEMENTED
   - USB temperature/humidity sensor monitoring with immediate reconnection
   - Sensor calibration validation and automatic recalibration
   - Backup sensor readings from multiple sources when available
   - Sensor communication protocol recovery (USB, I2C, etc.)

5. **🔄 Smart Plug & Zigbee Recovery** (5-45 seconds): NEXT PHASE
   - Zigbee network health monitoring with automatic mesh repair
   - Smart plug connectivity checks every 30 seconds
   - Power state verification and automatic restoration
   - Zigbee coordinator restart and device re-pairing as needed
   - Emergency manual override activation during extended outages

6. **✅ Home Assistant Core Recovery** (30-60 seconds): IMPLEMENTED
   - Docker container health monitoring with automatic restart
   - Database integrity checks and automatic repair
   - Configuration validation before service restart
   - Integration health monitoring with selective restart
   - Core service dependency management and restoration

7. **✅ Hardware-Level Monitoring**: IMPLEMENTED
   - USB touchscreen connection monitoring with auto-reconnect
   - HDMI display connection health checks
   - Power management to prevent display sleep/timeout issues
   - USB hub power cycling for unresponsive devices
   - System temperature monitoring to prevent overheating

### Recovery Implementation Requirements:
- **✅ Immediate Restart**: ALL services configured with `Restart=always` and appropriate `RestartSec` - IMPLEMENTED
- **✅ Comprehensive Health Monitoring**: IMPLEMENTED
  - Display responsiveness: every 30 seconds
  - Temperature/humidity sensors: every 60 seconds
  - Smart plugs: every 30 seconds (ready for implementation)
  - Camera feed: every 60 seconds (ready for implementation)
  - Zigbee network: every 2 minutes (ready for implementation)
  - Home Assistant core: every 5 minutes
- **✅ Rapid Recovery**: Maximum downtime specified per component (see goals above) - IMPLEMENTED
- **🔄 Emergency Failsafes**: NEXT PHASE
  - Heating/cooling systems activate manual backup controls during outages
  - Critical alerts sent via multiple channels (mobile, email, on-screen)
  - Local data logging continues even during Home Assistant outages
- **✅ Comprehensive Logging**: All failures logged with severity levels and recovery actions - IMPLEMENTED
- **✅ Preemptive Maintenance**: Memory management, cache clearing, and database optimization - IMPLEMENTED
- **🔄 Fallback Systems**: Emergency displays and manual controls for all critical functions - NEXT PHASE

### Specific Systemd Configurations Needed:
```
# ✅ Critical Display Service - IMPLEMENTED
[Unit]
Description=Turtle Kiosk Display
After=graphical-session.target
Wants=graphical-session.target

[Service]
Restart=always
RestartSec=2
StartLimitIntervalSec=0
WatchdogSec=30

# ✅ Critical Sensor Monitoring - IMPLEMENTED
[Unit] 
Description=Turtle Environmental Sensors
After=usb.target

[Service]
Restart=always
RestartSec=5
WatchdogSec=60

# 🔄 Critical Smart Plug Control - NEXT PHASE
[Unit]
Description=Turtle Climate Control
After=network.target

[Service]
Restart=always
RestartSec=3
WatchdogSec=45

# All services: Type=simple, StartLimitIntervalSec=0
```

### Comprehensive Recovery Testing Requirements:
- **✅ Display System Tests**: Browser/X11 process kills, graphics driver crashes, touchscreen disconnections - COMPLETED
- **✅ Sensor System Tests**: USB sensor disconnections, driver failures, calibration corruption - COMPLETED
- **🔄 Smart Plug Tests**: Zigbee network disruption, coordinator failures, device unpairing - NEXT PHASE
- **🔄 Camera System Tests**: USB disconnections, stream failures, codec crashes - NEXT PHASE
- **✅ Home Assistant Tests**: Container crashes, database corruption, integration failures - COMPLETED
- **✅ Network Tests**: Complete network loss, partial connectivity, DNS failures - COMPLETED
- **✅ Power Tests**: Unexpected shutdowns, UPS failover, partial power loss - COMPLETED
- **✅ Load Tests**: 24/7 continuous operation, memory leak detection, thermal stress - COMPLETED
- **🔄 Failsafe Tests**: Manual override activation, emergency alert delivery, backup control systems - NEXT PHASE
- **🔄 Integration Tests**: Multiple simultaneous failures, cascading failure recovery - NEXT PHASE

**🚨 FAILURE IS NOT AN OPTION: This system monitors a living creature's environment**

## 🔧 CRITICAL: Sequential Development Approach

**⚠️ MANDATORY: Build sequentially, validate each step, avoid intractable problems**

### **Phase-by-Phase Implementation Strategy:**

**✅ Phase 1: Basic Kiosk & Display (COMPLETED)**
1. ✅ Install minimal X11 + lightweight desktop
2. ✅ Get Chromium kiosk mode running
3. ✅ Display a simple HTML page
4. ✅ VALIDATE: Can see basic interface on screen
5. ✅ Add basic systemd service for kiosk
6. ✅ VALIDATE: Kiosk starts automatically on boot

**✅ Phase 2: Home Assistant Core (COMPLETED)**
1. ✅ Get Home Assistant Docker container running
2. ✅ Access HA from kiosk browser (simple dashboard)
3. ✅ VALIDATE: Can view Home Assistant interface on kiosk
4. ✅ Configure basic authentication/users
5. ✅ VALIDATE: Can log in and navigate HA

**✅ Phase 3: Environmental Sensor Integration (COMPLETED)**
1. ✅ **TEMPerHUM V4.1 Integration**: Complete sensor communication and MQTT publishing
2. ✅ **Home Assistant Auto-Discovery**: Sensors appear automatically with proper entities
3. ✅ **Production Service**: Systemd service with comprehensive logging and recovery
4. ✅ **Automated Deployment**: One-command deployment script with complete setup
5. ✅ **Dual Sensor Support**: Both shell and enclosure sensors working independently
6. ✅ VALIDATE: Temperature and humidity readings visible in Home Assistant

**🔄 Phase 4: Smart Plug Integration (NEXT PHASE)**
1. **First**: Add ONE smart plug
2. **VALIDATE**: Can control the smart plug from HA
3. **Second**: Add remaining smart plugs
4. **VALIDATE**: All smart plugs controllable from HA
5. **Third**: Add energy monitoring
6. **VALIDATE**: Power consumption data visible in HA

**🔄 Phase 5: Camera Integration (NEXT PHASE)**
1. **First**: Add Arducam camera
2. **VALIDATE**: Can see camera feed in HA
3. **Second**: Add motion detection
4. **VALIDATE**: Motion events trigger in HA
5. **Third**: Add recording capabilities
6. **VALIDATE**: Video recording works properly

**🔄 Phase 6: Basic Automations (NEXT PHASE)**
1. Add simple temperature alert automation
2. **VALIDATE**: Gets alert when temperature out of range
3. Add basic smart plug automation
4. **VALIDATE**: Smart plug responds to temperature
5. Test manual override controls
6. **VALIDATE**: Can manually control everything

**🔄 Phase 7: Reliability Features (NEXT PHASE)**
1. Add systemd restart policies ONE service at a time
2. Add basic monitoring scripts
3. Test recovery by manually killing processes
4. **VALIDATE**: Each service restarts correctly
5. Gradually add more sophisticated monitoring

### **Development Rules to Prevent Intractable Problems:**

1. **ONE THING AT A TIME**: Never add multiple new components simultaneously
2. **VALIDATE BEFORE PROCEEDING**: Every step must work 100% before moving forward
3. **KEEP CONFIGS SIMPLE**: Start with minimal configurations, add complexity later
4. **COMMIT WORKING STATES**: Git commit after each successful validation step
5. **DOCUMENT WHAT WORKS**: Keep notes on each working configuration
6. **ROLLBACK CAPABILITY**: Always know how to get back to the last working state
7. **AVOID PREMATURE OPTIMIZATION**: Get basic functionality first, reliability second

### **When Things Go Wrong:**
- **Stop immediately** if something doesn't work as expected
- **Don't add more complexity** to try to fix issues
- **Isolate the problem** to the specific component that's failing
- **Test components individually** outside of the full system if needed
- **Consider reverting** to the last known working state rather than debugging for hours

### **Testing Each Phase:**
- **Manual Testing**: Physically verify each component works
- **Reboot Testing**: Ensure everything works after system restart
- **Basic Recovery**: Test that simple restarts work before adding complex recovery
- **User Interaction**: Verify touchscreen/interface works at each step

**🎯 SUCCESS METRIC: Each phase should be completely stable before moving to the next phase**

## 🔄 CRITICAL: Current Software Versions & Update Management

**📦 MANDATORY: Use latest stable versions of ALL software components for security and compatibility**

### **Required Version Standards:**

**Docker Containers:**
- **Home Assistant**: Use `homeassistant/home-assistant:latest` or current stable release
- **Base OS Images**: Ubuntu 22.04 LTS (current LTS) or newer
- **Web Browsers**: Latest Chromium from official repositories
- **Database**: Current PostgreSQL or MariaDB stable releases if using external DB

**System Software:**
- **Docker Engine**: Latest stable version (24.x+ as of 2024)
- **Docker Compose**: Latest stable version (v2.x+)
- **Python**: Python 3.11+ for any custom scripts
- **Node.js**: Current LTS version for any web components
- **Nginx/Apache**: Latest stable versions if using reverse proxy

**Home Assistant Integrations & Add-ons:**
- **HACS (Home Assistant Community Store)**: Latest version for custom components
- **Kiosk Mode**: Latest version from HACS or official source
- **Zigbee2MQTT**: Current stable release if using Zigbee integration
- **Camera Integrations**: Latest compatible versions for Arducam support
- **USB Sensor Integrations**: Current stable versions

**Hardware Drivers:**
- **USB Drivers**: Latest kernel drivers for Ubuntu 22.04+
- **Touchscreen Drivers**: Current stable drivers for 10.1" display
- **Camera Drivers**: Latest UVC drivers for USB cameras
- **Zigbee Drivers**: Current drivers for Sonoff dongle

### **Version Management Practices:**

**Container Version Pinning:**
```yaml
# Use specific versions in production, latest in development
services:
  homeassistant:
    image: homeassistant/home-assistant:2024.1.0  # Pin to specific version
    # image: homeassistant/home-assistant:latest   # For development only
```

**Regular Update Schedule:**
- **Security Updates**: Apply immediately when available
- **Home Assistant**: Update monthly during maintenance windows
- **Container Images**: Update quarterly or when security patches released
- **System Packages**: Update monthly with `apt update && apt upgrade`
- **Custom Components**: Update when new features needed or security patches available

**Pre-Update Testing:**
1. **Test in Development**: Never update production directly
2. **Backup Before Updates**: Complete system backup before any major updates
3. **Staged Rollout**: Update one component at a time
4. **Rollback Plan**: Always have tested rollback procedures
5. **Validation After Updates**: Verify all functions work after updates

### **Version Documentation Requirements:**
- **Version Manifest**: Document all software versions in repository
- **Update Log**: Track all version changes with dates and reasons
- **Compatibility Matrix**: Document tested version combinations
- **Known Issues**: Track any version-specific problems or workarounds

### **Automated Update Considerations:**
- **Security Patches**: Enable automatic security updates for base OS
- **Container Updates**: Use Watchtower or similar for non-critical containers
- **Manual Updates**: Always manually update Home Assistant and critical services
- **Update Notifications**: Set up alerts for available updates

**🔒 SECURITY PRIORITY: Outdated software is a security risk - keep everything current**

## 📹 CRITICAL: Camera Reliability & Recovery Requirements

**🎯 CAMERA GOAL: Live video feed must NEVER be down for more than 60 seconds**

### Camera Multi-Layer Recovery Architecture:
1. **USB Camera Recovery** (10-20 seconds):
   - USB device connection monitoring with automatic reconnection
   - Camera driver restart and reinitialization on failure
   - USB hub power cycling if camera becomes unresponsive
   - Automatic device permission restoration after reconnection

2. **Video Stream Recovery** (15-30 seconds):
   - RTSP/HTTP stream health monitoring with immediate restart
   - Video codec recovery and re-establishment
   - Stream buffer management to prevent memory leaks
   - Automatic stream quality adjustment if bandwidth issues detected

3. **Home Assistant Camera Integration Recovery** (20-45 seconds):
   - Camera entity monitoring with automatic re-detection
   - Integration service restart if camera feed fails
   - Device discovery refresh to re-establish connection
   - Camera configuration validation and repair

4. **Hardware-Level Camera Monitoring**:
   - USB power management to prevent camera sleep/disconnect
   - Physical USB connection integrity checking
   - Camera module temperature monitoring (prevent overheating)
   - LED status monitoring for camera health indication

### Camera Recovery Implementation Requirements:
- **USB Device Rules**: Comprehensive udev rules for automatic camera detection and permissions
- **Stream Redundancy**: Multiple stream formats (MJPEG, H.264) with automatic fallback
- **Health Checks**: Camera responsiveness testing every 60 seconds
- **Automatic Restart**: Camera services configured with `Restart=always` and rapid restart
- **Error Logging**: All camera failures logged with Home Assistant alerts
- **Night Vision**: Ensure IR capability works continuously in low-light conditions
- **Emergency Placeholder**: Static "Camera Offline" image if all recovery attempts fail

### Specific Camera Systemd Service Configuration:
```
[Unit]
Description=Turtle Camera Service
After=usb.target
Requires=usb.target

[Service]
Restart=always
RestartSec=5
StartLimitIntervalSec=0
WatchdogSec=60
Type=simple
```

### Camera Recovery Testing Requirements:
- **USB Disconnect Tests**: Verify rapid camera reconnection and stream restoration
- **Process Kill Tests**: Camera service restart verification
- **Driver Crash Tests**: Complete camera stack recovery testing
- **Power Cycle Tests**: Camera functionality after system restart
- **Continuous Operation**: 24/7 stability testing with periodic stream quality validation
- **Network Interruption**: Stream recovery after Home Assistant connection loss

### Camera Integration Requirements:
- **Day/Night Transition**: Automatic IR switching without service interruption
- **Motion Detection**: Always-on motion sensing with failure recovery
- **Stream Quality**: Automatic bitrate adjustment for network conditions
- **Recording Continuity**: Local backup recording during any Home Assistant outages
- **Multiple Access**: Simultaneous dashboard viewing and mobile app access

**📹 CAMERA UPTIME TARGET: 99.9% availability with maximum 60-second recovery time**

## Development Environment
**Local Development Setup**: I'm developing locally and need all files organized for GitHub deployment
**Remote Target**: Ubuntu Server + Docker + Home Assistant container running on Beelink Mini PC
**Deployment Method**: Git pull from repository to remote machine

### Repository Structure Needed:
- **Version Documentation**: Manifest files listing all software versions and compatibility matrix
- **Home Assistant configs**: YAML files with template placeholders for secrets (automations, integrations, dashboard configurations)
- **Secret templates**: Template files showing required secrets without exposing actual values
- **Docker configs**: Container configurations with pinned versions and secure secret mounting
- **Kiosk setup scripts**: Systemd services, display configuration, auto-start scripts using current software
- **Security scripts**: Interactive setup scripts for secrets management and secure deployment
- **Custom themes**: CSS files for turtle-themed interface compatible with latest HA versions
- **Hardware configs**: Udev rules, USB device configurations for current drivers
- **Update scripts**: Automated update procedures with testing and rollback capabilities
- **Documentation**: Comprehensive setup instructions including version management and secrets procedures

### Development Goals:
- Create all configuration files that can be version controlled (with secrets as templates only)
- Use current, stable versions of all software components with proper documentation
- Implement secure secrets management that never exposes sensitive data to GitHub
- Organize files in a clear repository structure for easy and secure deployment
- Include secure deployment scripts with interactive secrets setup and version checking
- Ensure configurations work with the specific hardware and current software versions
- Provide comprehensive documentation including version management and security best practices

## System Architecture Priorities

**🐢 LIFE-CRITICAL SYSTEM: Every component is vital for turtle health and safety**

- **✅ Complete System Reliability**: Core components have bulletproof recovery with specific maximum downtimes:
  - ✅ Environmental sensors (temp/humidity): 30-second max recovery - IMPLEMENTED
  - 🔄 Smart plug controls (heating/cooling): 15-second max recovery - NEXT PHASE
  - ✅ Display monitoring interface: 30-second max recovery - IMPLEMENTED
  - 🔄 Camera surveillance: 60-second max recovery - NEXT PHASE
  - 🔄 Zigbee network: 45-second max recovery - NEXT PHASE
  - ✅ Home Assistant core: 60-second max recovery - IMPLEMENTED

- **🔄 Emergency Failsafes**: Manual backup controls activate immediately during system failures - NEXT PHASE
- **✅ Multi-Layer Recovery**: Hardware→Software→Service→Network recovery with rapid failover - IMPLEMENTED
- **✅ Comprehensive Health Monitoring**: All components monitored with appropriate intervals - IMPLEMENTED
- **✅ Security**: Secrets management, secure deployment, no sensitive data in version control - IMPLEMENTED
- **✅ Container Isolation**: Home Assistant and services in Docker with secure secret mounting - IMPLEMENTED
- **✅ Hardware Resilience**: Bulletproof USB device mapping with automatic recovery - IMPLEMENTED
- **✅ Preemptive Maintenance**: Proactive memory management, cache clearing, database optimization - IMPLEMENTED
- **🔄 Alert Redundancy**: Multiple notification channels for critical failures - NEXT PHASE
- **✅ Local Data Continuity**: Logging continues even during Home Assistant outages - IMPLEMENTED
- **✅ Current Software Versions**: Use latest stable versions of all components for security and compatibility - IMPLEMENTED
- **✅ Zero-Downtime Updates**: System updates without affecting turtle environment monitoring - IMPLEMENTED
- **✅ Version Management**: Proper documentation and testing of all software versions - IMPLEMENTED

## Design Aesthetic Goals
- **✅ Color Scheme**: Natural earth tones (forest green, warm browns, shell amber, water blue) - IMPLEMENTED
- **✅ Visual Elements**: Turtle shell patterns, leaf shapes, water ripples, organic curves - IMPLEMENTED
- **✅ Icons**: Custom turtle-themed icons for temperature (turtle with thermometer), humidity (turtle with water drops), power (turtle with leaf), camera (turtle eye), etc. - IMPLEMENTED
- **✅ Animations**: Subtle nature-inspired movements (gentle leaf sway, water ripples, soft shell patterns) - IMPLEMENTED
- **✅ Typography**: Friendly, readable fonts that complement the natural theme - IMPLEMENTED
- **✅ Layout**: Organic, flowing layouts that avoid harsh geometric shapes - IMPLEMENTED
- **✅ Status Indicators**: Shell-pattern progress bars, leaf-shaped buttons, water-drop humidity indicators - IMPLEMENTED

## User Experience Priority
This system is being built for a non-technical user who will primarily interact through the touchscreen. The interface must be:
- **✅ Intuitive**: Large buttons, clear labels, obvious functionality - IMPLEMENTED
- **✅ Reliable**: Auto-recovery from errors, graceful failure handling - IMPLEMENTED
- **✅ Visual**: Prominent displays of critical information (temperature, humidity, camera) - IMPLEMENTED
- **✅ Simple**: Minimal complexity, essential functions only - IMPLEMENTED
- **✅ Responsive**: Fast touch response, immediate visual feedback - IMPLEMENTED
- **🔄 Connected**: Easy mobile app setup with clear notification management - NEXT PHASE
- **🔄 Informative**: Notification history accessible via touchscreen with simple alert acknowledgment - NEXT PHASE
- **✅ Delightful**: Beautiful turtle-themed design that creates emotional connection and joy - IMPLEMENTED
- **✅ Natural**: Interface that feels organic and connects the user to their pet's natural habitat needs - IMPLEMENTED

I need help developing all the configuration files and scripts locally that I can then push to GitHub and deploy on the remote machine. Please provide:

1. **Repository Structure** - How to organize all files for easy deployment
2. **Configuration Files** - All YAML, CSS, and config files needed
3. **Deployment Scripts** - Scripts the remote machine can run after pulling from GitHub
4. **Clear Instructions** - Step-by-step deployment guide for the remote machine

**Sequential Development Priority (Build in Order, Validate Each Phase):**

**✅ PHASE 1: Basic Foundation (COMPLETED)**
1. **✅ Basic Kiosk Setup** - Latest X11, desktop, and current Chromium working with simple HTML display
2. **✅ Home Assistant Core** - Latest stable HA running in Docker with basic web interface accessible from kiosk
3. **✅ Security & Secrets Management** - Secure deployment scripts and secret templates using current tools
4. **✅ Environmental Sensor Integration** - TEMPerHUM V4.1 sensors fully integrated with MQTT auto-discovery

**🔄 PHASE 2: Smart Plug Integration (NEXT PHASE)**
4. **🔄 Smart Plug Integration** - Add ONE smart plug, get basic control working
5. **🔄 Energy Monitoring** - Add power consumption monitoring to smart plugs
6. **🔄 Additional Smart Plugs** - Add remaining smart plugs only after first one works

**🔄 PHASE 3: Camera Integration (NEXT PHASE)**
7. **🔄 Camera System** - Add Arducam camera, get video feed displaying in HA
8. **🔄 Motion Detection** - Add motion detection capabilities
9. **🔄 Recording Features** - Add video recording and storage

**🔄 PHASE 4: Basic Automations (NEXT PHASE)**
10. **🔄 Simple Environmental Automations** - Basic temperature/humidity alerts and responses
11. **🔄 Manual Override Controls** - Touch-friendly manual controls for all devices
12. **🔄 Basic Alert System** - Simple notifications for critical conditions

**🔄 PHASE 5: Reliability & Recovery (NEXT PHASE)**
13. **🔄 Gradual Reliability Features** - Add systemd restart policies and basic monitoring
14. **🔄 Recovery Testing** - Test and validate recovery mechanisms for each component
15. **🔄 Advanced Monitoring** - Add comprehensive health monitoring and failover systems

**🔄 RULE: Complete each phase 100% before starting the next. Commit working states frequently.**

**Important**: All files should be designed to work when deployed to the remote Ubuntu Server machine via git pull. Focus on creating a complete, deployable repository structure with robust security measures.

**Security Reminder**: Never commit actual secrets to GitHub. All sensitive data must use template files, environment variables, or interactive setup scripts.

What repository structure and configuration files should I create to implement the NEXT PHASE (Smart Plug Integration), building on the existing foundation of TEMPerHUM sensors and secure kiosk implementation, using the latest stable versions of all software components, ensuring each step works completely before proceeding to camera integration? Focus on getting smart plug control working reliably first, then we'll add camera integration in the subsequent phase.