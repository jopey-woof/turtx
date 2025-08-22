# 🐢 TemperhUM Sensor Integration for Turtle Monitoring

## Overview

This integration provides **production-ready TemperhUM USB sensor support** for the turtle monitoring system. It includes:

- **Automatic sensor discovery** and data reading
- **MQTT integration** with Home Assistant auto-discovery  
- **Systemd service** for reliable background operation
- **Zero-touch deployment** via automated setup script
- **Robust error handling** and logging

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  TemperhUM      │    │  MQTT Service    │    │  Home Assistant │
│  USB Sensors    │───▶│  (Python)        │───▶│  via MQTT       │
│  (2x sensors)   │    │                  │    │  Auto-discovery │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Features

### ✅ **Sensor Communication**
- **TEMPerHUM V4.1 support** - First implementation for this firmware version
- **Dual sensor support** - Independent reading from both sensors
- **HID protocol** - Direct USB HID communication using proven temper-py methods
- **Automatic discovery** - Detects sensors via USB VID:PID (3553:a001)

### ✅ **Home Assistant Integration**
- **MQTT auto-discovery** - Sensors appear automatically in HA
- **Device grouping** - Sensors grouped as "Turtle Enclosure Sensors"
- **Proper device classes** - Temperature and humidity with correct units
- **Availability monitoring** - Online/offline status tracking

### ✅ **Production Ready**
- **Systemd service** - Runs as background service with auto-restart
- **Logging** - Comprehensive logging with log rotation
- **Error recovery** - Automatic retry on sensor failures
- **Security** - Runs as dedicated service user with minimal privileges

## Quick Start

### 1. Deploy the Integration

```bash
# Run the automated deployment script
sudo /home/shrimp/turtle-monitor/setup/deploy-temperhum.sh
```

This script will:
- ✅ Install system dependencies
- ✅ Create service user and permissions
- ✅ Setup USB device access rules
- ✅ Install Python environment and dependencies
- ✅ Create and start systemd service
- ✅ Configure logging and monitoring

### 2. Verify Installation

```bash
# Check service status
sudo systemctl status temperhum-mqtt

# View live logs
sudo journalctl -u temperhum-mqtt -f

# Test sensor connectivity
sudo /home/shrimp/turtle-monitor/setup/deploy-temperhum.sh test
```

### 3. Check Home Assistant

After deployment, the following entities will appear in Home Assistant:

- **Turtle Shell Temperature** (`sensor.turtle_shell_temperature`)
- **Turtle Shell Humidity** (`sensor.turtle_shell_humidity`)
- **Turtle Enclosure Temperature** (`sensor.turtle_enclosure_temperature`)
- **Turtle Enclosure Humidity** (`sensor.turtle_enclosure_humidity`)

## Configuration

### Service Configuration

Edit `/home/shrimp/turtle-monitor/hardware/temperhum_config.json`:

```json
{
  "mqtt": {
    "host": "localhost",
    "port": 1883,
    "username": null,
    "password": null
  },
  "sensors": {
    "sensor1": {
      "name": "Turtle Shell",
      "location": "shell"
    },
    "sensor2": {
      "name": "Turtle Enclosure",
      "location": "enclosure"
    }
  },
  "service": {
    "update_interval": 30,
    "retry_attempts": 3,
    "retry_delay": 5
  }
}
```

### Home Assistant Configuration

The integration uses MQTT auto-discovery, so **no manual configuration** is needed in Home Assistant. However, you can customize the entities:

```yaml
# configuration.yaml (optional customization)
sensor:
  - platform: mqtt
    name: "Shell Temperature"
    state_topic: "turtle/sensors/sensor1/temperature"
    unit_of_measurement: "°C"
    device_class: temperature
```

## MQTT Topics

### Discovery Topics (Auto-configured)
- `homeassistant/sensor/turtle_sensors_sensor1_temp/config`
- `homeassistant/sensor/turtle_sensors_sensor1_hum/config`
- `homeassistant/sensor/turtle_sensors_sensor2_temp/config`
- `homeassistant/sensor/turtle_sensors_sensor2_hum/config`

### Data Topics
- `turtle/sensors/sensor1/temperature` - Shell temperature (°C)
- `turtle/sensors/sensor1/humidity` - Shell humidity (%)
- `turtle/sensors/sensor2/temperature` - Enclosure temperature (°C)
- `turtle/sensors/sensor2/humidity` - Enclosure humidity (%)

### Availability Topics
- `turtle/sensors/sensor1/availability` - online/offline
- `turtle/sensors/sensor2/availability` - online/offline

## Troubleshooting

### Service Issues

```bash
# Check service status
sudo systemctl status temperhum-mqtt

# View detailed logs
sudo journalctl -u temperhum-mqtt -n 50

# Restart service
sudo systemctl restart temperhum-mqtt

# Test sensors manually
cd /home/shrimp/turtle-monitor/hardware
sudo python3 temperhum_mqtt_service.py --test
```

### USB Permission Issues

```bash
# Check USB devices
lsusb | grep 3553

# Check hidraw devices
ls -la /dev/hidraw*

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### MQTT Connection Issues

```bash
# Test MQTT broker
mosquitto_pub -h localhost -t test -m "hello"
mosquitto_sub -h localhost -t test

# Check MQTT logs
docker logs mqtt
```

### Home Assistant Not Showing Sensors

1. **Restart Home Assistant** after service deployment
2. **Check MQTT integration** in HA is enabled
3. **Verify MQTT topics** are being published:
   ```bash
   mosquitto_sub -h localhost -t turtle/sensors/+/+
   ```

## Technical Details

### Sensor Communication Protocol

The integration uses the **proven temper-py HID protocol**:

```python
# Firmware query
firmware_query = struct.pack('8B', 0x01, 0x86, 0xff, 0x01, 0, 0, 0, 0)

# Data query
data_query = struct.pack('8B', 0x01, 0x80, 0x33, 0x01, 0, 0, 0, 0)

# Data parsing (TEMPerHUM_V4.1)
temperature = struct.unpack_from('>h', data_bytes, 2)[0] / 100.0
humidity = struct.unpack_from('>h', data_bytes, 4)[0] / 100.0
```

### File Structure

```
turtle-monitor/
├── hardware/
│   ├── temperhum_controller.py      # Core sensor communication
│   ├── temperhum_mqtt_service.py    # MQTT service
│   ├── temperhum_config.json        # Service configuration
│   └── temperhum_env/               # Python virtual environment
├── setup/
│   └── deploy-temperhum.sh          # Deployment script
└── docker/
    └── docker-compose.yml           # Updated with USB device mapping
```

### Service Files

- **Systemd service**: `/etc/systemd/system/temperhum-mqtt.service`
- **USB permissions**: `/etc/udev/rules.d/99-temperhum.rules`
- **Log rotation**: `/etc/logrotate.d/temperhum`

## Maintenance

### Log Management

```bash
# View current logs
sudo journalctl -u temperhum-mqtt -f

# Check log files
sudo tail -f /var/log/temperhum-mqtt.log

# Log rotation is automatic (daily, 7 days retention)
```

### Service Management

```bash
# Start/stop/restart service
sudo systemctl start temperhum-mqtt
sudo systemctl stop temperhum-mqtt
sudo systemctl restart temperhum-mqtt

# Enable/disable auto-start
sudo systemctl enable temperhum-mqtt
sudo systemctl disable temperhum-mqtt
```

### Updates

To update the sensor service:

```bash
# Pull latest code
cd /home/shrimp/turtle-monitor
git pull

# Redeploy
sudo setup/deploy-temperhum.sh

# Service will be automatically restarted
```

## Security

The service follows security best practices:

- **Dedicated user**: Runs as `temperhum` user (not root)
- **Minimal privileges**: Only access to required USB devices
- **Isolated environment**: Python virtual environment
- **Protected directories**: Read-only access where possible
- **No network privileges**: Only local MQTT access

## Support

### Logs Location
- **Service logs**: `journalctl -u temperhum-mqtt`
- **Application logs**: `/var/log/temperhum-mqtt.log`

### Common Commands
```bash
# Service status
sudo /home/shrimp/turtle-monitor/setup/deploy-temperhum.sh status

# Restart service
sudo /home/shrimp/turtle-monitor/setup/deploy-temperhum.sh restart

# View logs
sudo /home/shrimp/turtle-monitor/setup/deploy-temperhum.sh logs

# Test sensors
sudo /home/shrimp/turtle-monitor/setup/deploy-temperhum.sh test
```

---

**🎉 Integration Complete!** The TemperhUM sensors are now fully integrated into the turtle monitoring system with automatic Home Assistant discovery and production-ready reliability.