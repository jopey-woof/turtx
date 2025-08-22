# 🐢 Turtle Enclosure Monitoring System

A comprehensive IoT monitoring system for turtle enclosures, featuring temperature/humidity monitoring, automated environmental control, and a beautiful kiosk interface.

## 🚀 Quick Start

### Complete System Setup
```bash
# Bootstrap the entire system
./setup/bootstrap.sh

# Apply the turtle theme
./setup/apply-theme.sh
```

## 🎯 Features

### 🌡️ Temperature & Humidity Monitoring
- **TEMPerHUM USB Sensors**: Programmatic control and automatic data collection
- **Interval-Based Identification**: Smart sensor differentiation (1S vs 2S intervals)
- **Real-time Data**: Continuous monitoring with MQTT integration
- **Home Assistant Integration**: Automatic sensor discovery and dashboard creation

### 🖥️ Kiosk Interface
- **Touchscreen Optimized**: Designed for 1024x600 displays
- **Dark Theme**: Easy on the eyes with turtle-inspired colors
- **Auto-login**: Seamless user experience
- **Virtual Keyboard**: Touch-friendly input

### 🔧 Automation
- **Environmental Control**: Automated temperature and humidity management
- **Alert System**: Notifications for critical conditions
- **Data Logging**: Historical data collection and analysis
- **System Monitoring**: Health checks and automatic recovery

## 📁 Project Structure

```
turtle-monitor/
├── setup/                         # System setup and installation scripts
│   ├── bootstrap.sh              # Initial system setup
│   ├── install-temperhum.sh      # TEMPerHUM sensor installation
│   └── test-temperhum.sh         # Sensor testing and validation
├── hardware/                      # Hardware device configurations
│   ├── temperhum_manager.py      # TEMPerHUM sensor manager
│   ├── temperhum-manager.service # Systemd service
│   ├── 99-temperhum.rules        # Udev rules for USB devices
│   └── validate_temperhum.py     # Local validation script
├── homeassistant/                 # Home Assistant configurations
│   ├── configuration.yaml        # Main HA config
│   ├── sensors.yaml              # TEMPerHUM sensor definitions
│   └── lovelace/
│       └── dashboard.yaml        # Kiosk dashboard
├── kiosk/                         # Kiosk mode configurations
│   ├── kiosk.service            # Systemd service
│   └── start-kiosk.sh           # Kiosk startup script
└── docs/                          # Documentation
    ├── TEMPERHUM-IMPLEMENTATION.md    # Technical implementation guide
    ├── TEMPERHUM-SETUP-GUIDE.md       # End-user setup guide
    └── TEMPERHUM-IMPLEMENTATION-SUMMARY.md # Implementation summary
```

## 🖥️ Kiosk Interface

### Features
- **Dark Theme**: Easy on the eyes with nature-inspired colors
- **Touch Optimized**: Designed for 1024x600 touchscreen displays
- **Auto-login**: Seamless user experience
- **Responsive Design**: Adapts to different screen sizes

### Setup
```bash
# Apply the turtle theme
./setup/apply-theme.sh

# Start kiosk mode
sudo systemctl start kiosk.service
```

## 🔧 System Requirements

### Hardware
- **Ubuntu Server 24.04+**: Base operating system
- **TEMPerHUM USB Sensors**: Temperature/humidity monitoring
- **Touchscreen Display**: 1024x600 or higher resolution
- **USB Camera**: Arducam 1080P for monitoring
- **Zigbee Dongle**: Sonoff for smart device control

### Software
- **Python 3.8+**: Core application runtime
- **Home Assistant**: Home automation platform
- **Mosquitto**: MQTT broker for sensor data
- **Docker**: Containerized deployment

## 📚 Documentation

### System Documentation
- **[Deployment Guide](docs/PHASE1-DEPLOYMENT.md)**: Complete system deployment
- **[Hardware Setup](docs/HARDWARE.md)**: Hardware configuration and testing

## 🧪 Testing

### System Testing
```bash
# Validate Phase 1 deployment
./setup/validate-phase1.sh

# Test kiosk functionality
./kiosk/test-keyboard.sh
```

## 🔍 Troubleshooting

### General System
```bash
# Check Home Assistant status
docker ps | grep homeassistant

# View system logs
sudo journalctl -u kiosk.service -f

# Test network connectivity
ping 10.0.20.69
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐢 About

This project was created to provide comprehensive monitoring and automation for turtle enclosures, ensuring optimal environmental conditions for turtle health and well-being.

---

**🐢 Happy turtle monitoring!**
