# 🐢 Eastern Box Turtle Monitoring System

A comprehensive IoT monitoring system for eastern box turtle habitat management, built with Home Assistant, Docker, and touchscreen kiosk interface.

## 🎯 Project Overview

This system monitors and controls the environmental conditions of an eastern box turtle enclosure using:
- **10.1" Touchscreen Kiosk** - Primary interface for monitoring and control
- **Home Assistant** - Core automation and monitoring platform  
- **Docker** - Containerized deployment for reliability
- **Zigbee Smart Plugs** - Climate control device management
- **Environmental Sensors** - Temperature and humidity monitoring
- **USB Camera** - Live habitat surveillance
- **Email & Mobile Alerts** - Critical condition notifications

## 🚀 Quick Start - Phase 1 Only

**⚠️ IMPORTANT: Build sequentially. Complete Phase 1 before adding hardware.**

### Prerequisites
- Ubuntu Server 22.04 LTS (Beelink Mini PC)
- SSH access to remote machine
- Internet connection
- 10.1" touchscreen display connected

### 1. Clone Repository
```bash
ssh shrimp@10.0.20.69
cd /home/shrimp
git clone https://github.com/YOUR_USERNAME/turtle-monitor.git
cd turtle-monitor
```

### 2. Configure Secrets
```bash
# Interactive secrets setup - you'll be prompted for passwords
./setup/setup-secrets.sh
```

### 3. Deploy Phase 1 Foundation  
```bash
# Make scripts executable
chmod +x setup/*.sh kiosk/*.sh

# Run bootstrap setup
./setup/bootstrap.sh
```

### 4. Validate Phase 1 ✅
Follow the comprehensive validation checklist in [Phase 1 Deployment Guide](docs/PHASE1-DEPLOYMENT.md)

**🛑 DO NOT proceed to Phase 2 until Phase 1 is 100% validated and stable for 48+ hours.**

## 📁 Repository Structure

```
turtle-monitor/
├── setup/                     # System setup scripts
│   ├── bootstrap.sh           # Main Phase 1 setup
│   ├── setup-secrets.sh       # Interactive secrets configuration  
│   ├── install-docker.sh      # Docker installation
│   └── install-display.sh     # Kiosk display setup
├── docker/
│   └── docker-compose.yml     # Home Assistant container config
├── homeassistant/             # Home Assistant configurations
│   ├── configuration.yaml     # Main HA configuration
│   ├── automations.yaml       # System automations
│   ├── sensors.yaml          # Sensor definitions
│   ├── scripts.yaml          # System control scripts
│   └── lovelace/             # Dashboard configurations
│       ├── dashboard.yaml    # Turtle-themed kiosk dashboard
│       └── themes/
│           └── turtle-theme.yaml  # Custom turtle theme
├── kiosk/                     # Kiosk mode configurations
│   ├── start-kiosk.sh        # Kiosk startup script
│   └── kiosk.service         # Systemd service configuration
└── docs/                      # Documentation
    └── PHASE1-DEPLOYMENT.md   # Detailed Phase 1 guide
```

## 🔐 Security & Secrets Management

**🚨 CRITICAL: Never commit real secrets to Git**

- **Environment Template**: `environment.template` shows required variables
- **Interactive Setup**: `setup/setup-secrets.sh` prompts for real values
- **Secure Storage**: Secrets stored in `.env` (git-ignored) with 600 permissions
- **Template Files**: All config files use placeholders, templates included

Required secrets:
- Home Assistant admin credentials  
- Email notification credentials (Gmail app password)
- WiFi network credentials
- Mobile app webhook IDs

## 🏗️ Development Phases

### ✅ Phase 1: Foundation (Current)
- [x] Basic kiosk display system
- [x] Home Assistant core installation
- [x] Docker container orchestration  
- [x] Touchscreen interface
- [x] Basic turtle-themed dashboard
- [x] Email notification system
- [x] System health monitoring
- [x] Auto-start services

### 🔄 Phase 2: Hardware Integration (Next)
- [ ] Arducam USB camera integration
- [ ] Sonoff Zigbee coordinator setup
- [ ] Smart plug device pairing
- [ ] Environmental monitoring automations
- [ ] Camera live feed integration

### 🔄 Phase 3: Advanced Features
- [ ] Advanced automations & alerts
- [ ] Mobile app configuration
- [ ] Historical data visualization  
- [ ] Equipment failure detection
- [ ] Emergency control systems

### 🔄 Phase 4: Reliability & Recovery
- [ ] Multi-layer recovery systems
- [ ] Hardware health monitoring
- [ ] Automated failover systems
- [ ] Comprehensive testing

## 🎨 Design Philosophy

**Turtle-Themed Interface:**
- Earth tone color palette (forest green, warm browns, shell amber)
- Organic, curved design elements
- Custom turtle and nature-themed icons
- Touch-optimized controls (1024x600 display)
- Delightful user experience connecting users to nature

**Reliability-First Architecture:**
- Sequential development preventing intractable problems
- Comprehensive validation at each phase
- Life-critical system design (turtle's health depends on it)
- Multi-layer recovery with specific downtime limits
- Hardware monitoring and automatic failover

## 📊 System Specifications

**Target Environment:**
- **Host**: Beelink Mini PC (Ubuntu Server 22.04 LTS)
- **Display**: 10.1" touchscreen (1024x600 IPS)
- **Camera**: Arducam 1080P USB with day/night vision
- **Zigbee**: Sonoff Zigbee USB Dongle Plus
- **Smart Control**: 4x Zigbee smart plugs with energy monitoring
- **Primary Thermostat**: Vivarium Electronics VE-200 (existing)

**Software Stack:**
- **Home Assistant**: 2024.1.0+ (latest stable)
- **Docker**: Latest stable version
- **OS**: Ubuntu Server 22.04 LTS
- **Browser**: Latest Chromium (kiosk mode)
- **Desktop**: Openbox (minimal)

## 📞 Support & Troubleshooting

**Phase 1 Issues:**
1. Check service logs: `sudo journalctl -u kiosk.service -f`
2. Verify Home Assistant: `docker-compose logs homeassistant`
3. Test display: `export DISPLAY=:0 && chromium-browser http://localhost:8123`
4. Validate secrets: Check `.env` file has correct values

**Getting Help:**
- Review [Phase 1 Deployment Guide](docs/PHASE1-DEPLOYMENT.md)
- Check troubleshooting section for common issues
- Verify all validation steps pass before proceeding

## 🎯 Success Criteria - Phase 1

Before proceeding to hardware integration:

✅ **Automatic Boot**: Kiosk displays Home Assistant after reboot  
✅ **Touchscreen Control**: All interface elements work via touch  
✅ **Email Notifications**: Test alerts delivered successfully  
✅ **System Stability**: 48+ hours continuous operation  
✅ **Service Recovery**: Auto-restart after process termination  
✅ **Complete Validation**: All checklist items in deployment guide  

## ⚠️ Important Notes

- **Sequential Development**: Complete each phase before proceeding
- **Life-Critical System**: A living creature depends on this system
- **No Shortcuts**: Validate everything thoroughly before adding complexity
- **Security First**: Never expose secrets in version control
- **Touch-Optimized**: All controls sized for finger navigation
- **Current Versions**: Always use latest stable software releases

---

**🐢 Built with love for our shelled friends**

This system prioritizes the health and safety of eastern box turtles through reliable, automated environmental monitoring and control.