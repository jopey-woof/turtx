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
- **Ready to deploy**: All configurations I develop locally will be pulled to this machine

## Hardware Setup (Remote Machine)
- **Host**: Beelink Mini PC (running Ubuntu Server 22.04 LTS)
- **Display**: ROADOM 10.1" Touchscreen Monitor (1024×600 IPS) - Primary kiosk interface
- **Connectivity**: 3-foot Anker HDMI cable for display connection
- **Sensors**: TEMPerHUM PC USB sensor (temperature & humidity monitoring)
- **Camera**: Arducam 1080P Day & Night Vision USB Camera
- **Zigbee Hub**: Sonoff Zigbee USB Dongle Plus (ZBDongle-E 3.0)
- **Smart Control**: ZigBee Smart Plugs 4-pack with energy monitoring (15A outlets, Zigbee repeaters)
- **USB Expansion**: Anker 4-Port USB 3.0 Hub + AINOPE USB 3.0 extension cables
- **Primary Heat Control**: Vivarium Electronics VE-200 w/night drop (existing, reliable thermostat)

## Project Goals
1. **Touchscreen Kiosk Interface**: Create a simple, intuitive touchscreen dashboard for non-technical user operation
2. **Environmental Monitoring**: Track temperature and humidity with large, easy-to-read displays
3. **Smart Cooling Control**: Touch-controlled fans, misters, or cooling devices via Zigbee smart plugs
4. **Live Camera Feed**: Integrated video stream viewable on the touchscreen interface
5. **Energy Monitoring**: Display real-time power consumption from smart plugs
6. **Push Notifications**: Mobile app and email alerts for critical conditions and equipment failures
7. **Data Integration**: Monitor and log data while working alongside existing VE-200 heat controller
8. **Simple Device Control**: Large touch buttons for manual override of automated systems
9. **Visual Alerts**: Clear on-screen notifications for any issues or out-of-range conditions
10. **Beautiful Turtle Theming**: Create a visually stunning interface with turtle and nature-inspired design elements

## Specific Requirements
- Temperature range: 70-85°F (21-29°C) with basking spot up to 90°F (32°C)
- Humidity range: 60-80% for eastern box turtles
- Day/night lighting cycles
- **Critical Alert Scenarios**: Temperature outside safe range, humidity too low/high, equipment power failures, camera/sensor disconnection
- **Notification Preferences**: Tiered alerts (Critical/Warning/Info) with user-configurable settings
- **Delivery Methods**: Home Assistant mobile app (primary), email backup, on-screen kiosk alerts
- Historical data visualization and export capabilities
- **Equipment Failure Detection**: Monitor smart plug power consumption to detect device failures

## Secrets Management & Security Requirements

**⚠️ CRITICAL: All secrets must be kept out of GitHub repository and version control**

### Instructions for AI Assistant:
**When working with this prompt, you MUST:**
1. **Follow the sequential development approach** - Focus on ONE phase at a time, validate before proceeding
2. **Start with Phase 1 only** - Get basic kiosk + Home Assistant working before adding any hardware
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

## Technical Tasks I Need Help With

### Kiosk Display Setup
1. **Install Display Components**: Install X11, lightweight desktop environment, and Chromium for kiosk mode
2. **Touchscreen Configuration**: Set up touch input drivers and calibration for the 10.1" 1024×600 display
3. **Auto-boot Kiosk**: Create systemd services for automatic login and Chromium kiosk startup to display turtle dashboard by default
4. **Turtle Dashboard Auto-Launch**: Configure the system to automatically display the custom turtle-themed Home Assistant dashboard upon mini PC startup
5. **Multi-Layer Recovery System**: Implement comprehensive watchdog and recovery services for maximum uptime

### Life-Critical Hardware Integration
6. **Mission-Critical USB Device Management**: Configure bulletproof udev rules and permissions for ALL USB devices (sensors, camera) with automatic recovery and failover
7. **Zigbee Network Resilience**: Configure Sonoff dongle with mesh repair, coordinator backup, and automatic device re-pairing
8. **Environmental Sensor Reliability**: TEMPerHUM sensor integration with 30-second max recovery, calibration validation, and backup readings
9. **Climate Control Integration**: Smart plug configuration with 15-second max recovery, power state verification, and emergency manual override
10. **Camera Surveillance System**: Arducam integration with multi-layer recovery, stream redundancy, and 60-second maximum downtime

### Life-Critical Home Assistant Configuration
11. **Skip Onboarding Setup**: Configure Home Assistant to bypass initial onboarding wizard since kiosk won't have keyboard access
12. **Kiosk Mode Plugin**: Download, install, and properly configure the official Home Assistant 'Kiosk Mode' plugin for optimal touchscreen experience
13. **Mission-Critical Device Integrations**: YAML configurations for ALL sensors, camera, and Zigbee devices with health monitoring and failover
14. **Life-Critical Environmental Automations**: Temperature/humidity monitoring with immediate alerts and emergency responses
15. **Equipment Failure Detection**: Comprehensive automations to detect ALL device failures via power consumption, connectivity, and health checks
16. **Emergency Climate Control**: Smart plug automations with failsafes, manual overrides, and coordination with VE-200 thermostat
17. **Environmental Cycles**: Day/night lighting and temperature variations with backup controls and failure handling

### Life-Critical Alerts & Emergency Notifications
18. **Multi-Channel Alert System**: Configure immediate notifications via mobile app, email, and on-screen alerts for ALL critical failures
19. **Emergency Contact Escalation**: Progressive alert escalation for life-threatening conditions (temperature extremes, complete system failures)
20. **Critical Alert Automations**: Immediate alerts for environmental dangers, equipment failures, and system outages with severity-based responses
21. **Emergency Interface**: Touch-friendly emergency controls and alert acknowledgment with manual override capabilities

### Turtle-Themed Interface Design
22. **Custom Turtle Dashboard**: Create a dedicated turtle-themed Home Assistant dashboard as the primary interface
23. **Custom CSS Theme**: Create turtle-inspired colors, fonts, and styling optimized for 1024×600 touchscreen
24. **Custom Icons**: Implement turtle, leaf, water drop, and nature-themed icons throughout interface
25. **Touch-Optimized Layout**: Design large buttons and controls perfect for finger navigation
26. **Dashboard Cards**: Create beautiful cards for temperature, humidity, camera feed, and device status
27. **Animations**: Add subtle nature-themed animations (water ripples, gentle movements)
28. **Seasonal Themes**: Dynamic color schemes that change with day/night cycles

## ⚡ CRITICAL: Complete System Reliability & Recovery Requirements

**🐢 LIFE-CRITICAL SYSTEM: ALL components must have bulletproof reliability - a living creature depends on this**

**🎯 PRIMARY GOALS:**
- **Display**: Maximum 30-second recovery time
- **Camera**: Maximum 60-second recovery time  
- **Temperature Monitoring**: Maximum 30-second sensor recovery time
- **Humidity Monitoring**: Maximum 30-second sensor recovery time
- **Smart Plug Control**: Maximum 15-second recovery time (heating/cooling critical)
- **Zigbee Network**: Maximum 45-second recovery time
- **Home Assistant Core**: Maximum 60-second recovery time
- **All Environmental Controls**: Immediate failsafe activation during outages

### Multi-Layer Recovery Architecture:
1. **Browser-Level Recovery** (5-10 seconds):
   - Chromium process monitoring with immediate restart on crash
   - Automatic page refresh every 5 minutes to prevent browser memory issues
   - JavaScript-based page health monitoring and auto-reload

2. **X11/Display Recovery** (10-15 seconds):
   - X server watchdog service to restart display manager on failure
   - Automatic graphics driver recovery and reinitialization
   - Display connection monitoring for touchscreen disconnect/reconnect

3. **System-Level Recovery** (15-30 seconds):
   - Systemd service dependencies with automatic restart policies
   - Desktop environment watchdog with rapid restart capability
   - Complete kiosk stack restart as last resort

4. **Environmental Sensor Recovery** (10-30 seconds):
   - USB temperature/humidity sensor monitoring with immediate reconnection
   - Sensor calibration validation and automatic recalibration
   - Backup sensor readings from multiple sources when available
   - Sensor communication protocol recovery (USB, I2C, etc.)

5. **Smart Plug & Zigbee Recovery** (5-45 seconds):
   - Zigbee network health monitoring with automatic mesh repair
   - Smart plug connectivity checks every 30 seconds
   - Power state verification and automatic restoration
   - Zigbee coordinator restart and device re-pairing as needed
   - Emergency manual override activation during extended outages

6. **Home Assistant Core Recovery** (30-60 seconds):
   - Docker container health monitoring with automatic restart
   - Database integrity checks and automatic repair
   - Configuration validation before service restart
   - Integration health monitoring with selective restart
   - Core service dependency management and restoration

7. **Hardware-Level Monitoring**:
   - USB touchscreen connection monitoring with auto-reconnect
   - HDMI display connection health checks
   - Power management to prevent display sleep/timeout issues
   - USB hub power cycling for unresponsive devices
   - System temperature monitoring to prevent overheating

### Recovery Implementation Requirements:
- **Immediate Restart**: ALL services configured with `Restart=always` and appropriate `RestartSec`
- **Comprehensive Health Monitoring**: 
  - Display responsiveness: every 30 seconds
  - Temperature/humidity sensors: every 60 seconds
  - Smart plugs: every 30 seconds
  - Camera feed: every 60 seconds
  - Zigbee network: every 2 minutes
  - Home Assistant core: every 5 minutes
- **Rapid Recovery**: Maximum downtime specified per component (see goals above)
- **Emergency Failsafes**: 
  - Heating/cooling systems activate manual backup controls during outages
  - Critical alerts sent via multiple channels (mobile, email, on-screen)
  - Local data logging continues even during Home Assistant outages
- **Comprehensive Logging**: All failures logged with severity levels and recovery actions
- **Preemptive Maintenance**: Memory management, cache clearing, and database optimization
- **Fallback Systems**: Emergency displays and manual controls for all critical functions

### Specific Systemd Configurations Needed:
```
# Critical Display Service
[Unit]
Description=Turtle Kiosk Display
After=graphical-session.target
Wants=graphical-session.target

[Service]
Restart=always
RestartSec=2
StartLimitIntervalSec=0
WatchdogSec=30

# Critical Sensor Monitoring
[Unit] 
Description=Turtle Environmental Sensors
After=usb.target

[Service]
Restart=always
RestartSec=5
WatchdogSec=60

# Critical Smart Plug Control
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
- **Display System Tests**: Browser/X11 process kills, graphics driver crashes, touchscreen disconnections
- **Sensor System Tests**: USB sensor disconnections, driver failures, calibration corruption
- **Smart Plug Tests**: Zigbee network disruption, coordinator failures, device unpairing
- **Camera System Tests**: USB disconnections, stream failures, codec crashes
- **Home Assistant Tests**: Container crashes, database corruption, integration failures
- **Network Tests**: Complete network loss, partial connectivity, DNS failures
- **Power Tests**: Unexpected shutdowns, UPS failover, partial power loss
- **Load Tests**: 24/7 continuous operation, memory leak detection, thermal stress
- **Failsafe Tests**: Manual override activation, emergency alert delivery, backup control systems
- **Integration Tests**: Multiple simultaneous failures, cascading failure recovery

**🚨 FAILURE IS NOT AN OPTION: This system monitors a living creature's environment**

## 🔧 CRITICAL: Sequential Development Approach

**⚠️ MANDATORY: Build sequentially, validate each step, avoid intractable problems**

### **Phase-by-Phase Implementation Strategy:**

**Phase 1: Basic Kiosk & Display (Get working first)**
1. Install minimal X11 + lightweight desktop
2. Get Chromium kiosk mode running
3. Display a simple HTML page
4. ✅ VALIDATE: Can see basic interface on screen
5. Add basic systemd service for kiosk
6. ✅ VALIDATE: Kiosk starts automatically on boot

**Phase 2: Home Assistant Core (Add complexity gradually)**
1. Get Home Assistant Docker container running
2. Access HA from kiosk browser (simple dashboard)
3. ✅ VALIDATE: Can view Home Assistant interface on kiosk
4. Configure basic authentication/users
5. ✅ VALIDATE: Can log in and navigate HA

**Phase 3: Add ONE Hardware Component at a Time**
1. **First**: Add temperature sensor ONLY
2. ✅ VALIDATE: See temperature readings in HA
3. **Second**: Add humidity sensor (or same device if combined)
4. ✅ VALIDATE: See both temp + humidity readings
5. **Third**: Add ONE smart plug
6. ✅ VALIDATE: Can control the smart plug from HA
7. **Fourth**: Add camera
8. ✅ VALIDATE: Can see camera feed in HA

**Phase 4: Basic Automations (Keep simple)**
1. Add simple temperature alert automation
2. ✅ VALIDATE: Gets alert when temperature out of range
3. Add basic smart plug automation
4. ✅ VALIDATE: Smart plug responds to temperature
5. Test manual override controls
6. ✅ VALIDATE: Can manually control everything

**Phase 5: Reliability Features (Only after everything works)**
1. Add systemd restart policies ONE service at a time
2. Add basic monitoring scripts
3. Test recovery by manually killing processes
4. ✅ VALIDATE: Each service restarts correctly
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

- **Complete System Reliability**: ALL components have bulletproof recovery with specific maximum downtimes:
  - Environmental sensors (temp/humidity): 30-second max recovery
  - Smart plug controls (heating/cooling): 15-second max recovery  
  - Display monitoring interface: 30-second max recovery
  - Camera surveillance: 60-second max recovery
  - Zigbee network: 45-second max recovery
  - Home Assistant core: 60-second max recovery

- **Emergency Failsafes**: Manual backup controls activate immediately during system failures
- **Multi-Layer Recovery**: Hardware→Software→Service→Network recovery with rapid failover
- **Comprehensive Health Monitoring**: All components monitored with appropriate intervals
- **Security**: Secrets management, secure deployment, no sensitive data in version control
- **Container Isolation**: Home Assistant and services in Docker with secure secret mounting
- **Hardware Resilience**: Bulletproof USB device mapping with automatic recovery
- **Preemptive Maintenance**: Proactive memory management, cache clearing, database optimization
- **Alert Redundancy**: Multiple notification channels for critical failures
- **Local Data Continuity**: Logging continues even during Home Assistant outages
- **Current Software Versions**: Use latest stable versions of all components for security and compatibility
- **Zero-Downtime Updates**: System updates without affecting turtle environment monitoring
- **Version Management**: Proper documentation and testing of all software versions

## Design Aesthetic Goals
- **Color Scheme**: Natural earth tones (forest green, warm browns, shell amber, water blue)
- **Visual Elements**: Turtle shell patterns, leaf shapes, water ripples, organic curves
- **Icons**: Custom turtle-themed icons for temperature (turtle with thermometer), humidity (turtle with water drops), power (turtle with leaf), camera (turtle eye), etc.
- **Animations**: Subtle nature-inspired movements (gentle leaf sway, water ripples, soft shell patterns)
- **Typography**: Friendly, readable fonts that complement the natural theme
- **Layout**: Organic, flowing layouts that avoid harsh geometric shapes
- **Status Indicators**: Shell-pattern progress bars, leaf-shaped buttons, water-drop humidity indicators

## User Experience Priority
This system is being built for a non-technical user who will primarily interact through the touchscreen. The interface must be:
- **Intuitive**: Large buttons, clear labels, obvious functionality
- **Reliable**: Auto-recovery from errors, graceful failure handling
- **Visual**: Prominent displays of critical information (temperature, humidity, camera)
- **Simple**: Minimal complexity, essential functions only
- **Responsive**: Fast touch response, immediate visual feedback
- **Connected**: Easy mobile app setup with clear notification management
- **Informative**: Notification history accessible via touchscreen with simple alert acknowledgment
- **Delightful**: Beautiful turtle-themed design that creates emotional connection and joy
- **Natural**: Interface that feels organic and connects the user to their pet's natural habitat needs

I need help developing all the configuration files and scripts locally that I can then push to GitHub and deploy on the remote machine. Please provide:

1. **Repository Structure** - How to organize all files for easy deployment
2. **Configuration Files** - All YAML, CSS, and config files needed
3. **Deployment Scripts** - Scripts the remote machine can run after pulling from GitHub
4. **Clear Instructions** - Step-by-step deployment guide for the remote machine

**Sequential Development Priority (Build in Order, Validate Each Phase):**

**PHASE 1: Basic Foundation (Using Current Versions)**
1. **Basic Kiosk Setup** - Get latest X11, desktop, and current Chromium working with simple HTML display
2. **Home Assistant Core** - Get latest stable HA running in Docker with basic web interface accessible from kiosk
3. **Security & Secrets Management** - Set up secure deployment scripts and secret templates using current tools

**PHASE 2: Hardware Integration (One at a Time)**
4. **Environmental Sensors** - Add temperature/humidity sensor, get readings in HA
5. **Smart Plug Integration** - Add ONE smart plug, get basic control working
6. **Camera System** - Add camera, get video feed displaying in HA
7. **Additional Smart Plugs** - Add remaining smart plugs only after first one works

**PHASE 3: Basic Automations**
8. **Simple Environmental Automations** - Basic temperature/humidity alerts and responses
9. **Manual Override Controls** - Touch-friendly manual controls for all devices
10. **Basic Alert System** - Simple notifications for critical conditions

**PHASE 4: Turtle-Themed Interface**
11. **Custom Dashboard** - Create turtle-themed interface (only after all hardware works)
12. **Touch Optimization** - Optimize interface for touchscreen use

**PHASE 5: Reliability & Recovery (Last Step)**
13. **Gradual Reliability Features** - Add systemd restart policies and basic monitoring
14. **Recovery Testing** - Test and validate recovery mechanisms for each component
15. **Advanced Monitoring** - Add comprehensive health monitoring and failover systems

**🔄 RULE: Complete each phase 100% before starting the next. Commit working states frequently.**

**Important**: All files should be designed to work when deployed to the remote Ubuntu Server machine via git pull. Focus on creating a complete, deployable repository structure with robust security measures.

**Security Reminder**: Never commit actual secrets to GitHub. All sensitive data must use template files, environment variables, or interactive setup scripts.

What repository structure and configuration files should I create to implement PHASE 1 first (basic kiosk display + Home Assistant core), using the latest stable versions of all software components, ensuring each step works completely before proceeding to hardware integration? Focus on getting a simple, stable foundation working first with current versions, then we'll add hardware components one by one in subsequent phases.