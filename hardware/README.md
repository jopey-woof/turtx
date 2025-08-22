# 🐢 TemperhUM Hardware Integration

## Overview

This directory contains the **production-ready TemperhUM USB sensor integration** for the turtle monitoring system. The integration provides automatic sensor discovery, data reading, and MQTT publishing to Home Assistant.

## 🚀 Quick Start

Deploy the complete integration with a single command:

```bash
sudo /home/shrimp/turtle-monitor/setup/deploy-temperhum.sh
```

This automatically handles:
- ✅ System dependencies and permissions
- ✅ Python environment setup
- ✅ Systemd service creation
- ✅ USB device configuration
- ✅ MQTT integration with Home Assistant auto-discovery

## 📁 Production Files

### Core Components
- **`temperhum_controller.py`** - Sensor communication and data reading
- **`temperhum_mqtt_service.py`** - MQTT service with Home Assistant integration
- **`temperhum_config.json`** - Service configuration
- **`requirements.txt`** - Python dependencies

### Environment
- **`temperhum_env/`** - Python virtual environment (created during deployment)

### Development Archive
- **`archive/`** - Historical development and testing files (preserved for reference)

## 🔧 Service Management

```bash
# Service status
sudo systemctl status temperhum-mqtt

# View logs
sudo journalctl -u temperhum-mqtt -f

# Restart service
sudo systemctl restart temperhum-mqtt

# Quick deployment commands
sudo setup/deploy-temperhum.sh status
sudo setup/deploy-temperhum.sh test
sudo setup/deploy-temperhum.sh restart
```

## 📊 Home Assistant Integration

After deployment, these entities appear automatically in Home Assistant:

- **`sensor.turtle_shell_temperature`** - Shell temperature (°C)
- **`sensor.turtle_shell_humidity`** - Shell humidity (%)
- **`sensor.turtle_enclosure_temperature`** - Enclosure temperature (°C) 
- **`sensor.turtle_enclosure_humidity`** - Enclosure humidity (%)

## 🎯 Technical Specifications

### Supported Hardware
- **TEMPerHUM V4.1** USB sensors
- **VID:PID**: `3553:a001`
- **Protocol**: HID communication via `/dev/hidrawX`

### Data Format
```json
{
  "temperature_c": 28.97,
  "temperature_f": 84.146,
  "humidity": 36.25,
  "timestamp": 1755899839.638234
}
```

### MQTT Topics
- **Data**: `turtle/sensors/{sensor1|sensor2}/{temperature|humidity}`
- **Availability**: `turtle/sensors/{sensor1|sensor2}/availability`
- **Discovery**: Auto-configured for Home Assistant

## 📖 Documentation

For complete documentation, see:
- **[Integration Guide](../docs/TEMPERHUM_INTEGRATION.md)** - Complete setup and usage
- **[Integration Summary](../docs/INTEGRATION_COMPLETE.md)** - Achievement summary
- **[Technical Details](../docs/VICTORY_DOCUMENTATION.md)** - Protocol and implementation
- **[Integration Plan](../docs/HOME_ASSISTANT_INTEGRATION_PLAN.md)** - Development strategy

## 🎉 Status: Production Ready

This integration is **fully tested and production-ready** with:
- ✅ Automatic sensor discovery and communication
- ✅ Reliable MQTT publishing with Home Assistant auto-discovery
- ✅ Systemd service with auto-restart and logging
- ✅ Comprehensive error handling and recovery
- ✅ Zero-touch deployment automation
- ✅ Security best practices (dedicated user, minimal privileges)

**Ready for deployment to production turtle monitoring system!** 🐢