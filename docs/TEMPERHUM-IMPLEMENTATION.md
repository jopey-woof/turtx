# 🐢 TEMPerHUM USB Sensor Implementation

## Overview

This document describes the fresh implementation of TEMPerHUM USB temperature/humidity sensor integration for the Eastern Box Turtle monitoring system. This implementation replaces all previous TEMPerHUM work with a clean, robust solution.

## Architecture

### Components

1. **TEMPerHUM Manager** (`hardware/temperhum_manager.py`)
   - Python-based sensor management
   - Multi-sensor support (up to 2 sensors)
   - Robust initialization and activation
   - Error-resistant data parsing
   - MQTT integration for Home Assistant

2. **Systemd Service** (`hardware/temperhum-manager.service`)
   - Background service for automatic startup
   - Automatic restart on failure
   - Proper logging and monitoring

3. **Udev Rules** (`hardware/99-temperhum.rules`)
   - Device permissions for TEMPerHUM sensors
   - Automatic device detection and access

4. **Home Assistant Integration** (`homeassistant/sensors.yaml`)
   - MQTT-based sensor configuration
   - Temperature and humidity sensors
   - Celsius and Fahrenheit support

## Sensor Behavior

### Control Mechanism
- **Toggle Data Output**: Press and hold Caps Lock for 1 second to turn output ON/OFF
- **Increase Interval**: Double-press Caps Lock (increases by 1 second increments)  
- **Decrease Interval**: Double-press Num Lock (decreases by 1 second increments)
- **Initial State**: Unknown - sensors could be ON or OFF when system starts

### Data Output Format
When activated, sensors output a banner followed by continuous data:

**Banner Output:**
```
WWW.PCSENSOR.COM
TEMPERHUM V4.1
CAPS LOCK:ON/OFF/++
NUM LOCK:OFF/ON/-- 
TYPE:INNER-H3
INNER-TEMPINNER-HUMINTERVALWWW.PCSENSOR.COMTEMPERHUMV4.1CAPSLOCK:ON/OFF/++NUMLOCK:OFF/ON/--TYPE:INNER-H3INNER-TEMPINNER-HUMINTERVAL
```

**Continuous Data Format:**
```
29.54[C]39.58[%RH]1S
29.59[C]39.63[%RH]1S
27.60 [C]40.38[%RH]1S
```

## Installation

### Prerequisites
- Ubuntu Server 22.04 LTS or later
- Python 3.8+
- SSH access to remote server
- TEMPerHUM USB sensors (vendor ID: 3553, product ID: a001)

### Quick Installation

1. **Clean Previous Implementation**
   ```bash
   ./setup/cleanup-temperhum.sh
   ```

2. **Deploy to Remote Server**
   ```bash
   ./setup/deploy-temperhum.sh
   ```

### Manual Installation

1. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv python3-dev
   pip3 install --user paho-mqtt pyhidapi
   ```

2. **Install Udev Rules**
   ```bash
   sudo cp hardware/99-temperhum.rules /etc/udev/rules.d/
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   sudo usermod -a -G input $USER
   ```

3. **Install Systemd Service**
   ```bash
   sudo cp hardware/temperhum-manager.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable temperhum-manager.service
   ```

4. **Setup Logging**
   ```bash
   sudo touch /var/log/temperhum-manager.log
   sudo chown $USER:$USER /var/log/temperhum-manager.log
   ```

5. **Start Service**
   ```bash
   sudo systemctl start temperhum-manager.service
   ```

## Configuration

### MQTT Topics

The system publishes sensor data to the following MQTT topics:

- **Sensor 1**: `turtle/sensors/temperhum/sensor_1`
- **Sensor 2**: `turtle/sensors/temperhum/sensor_2`
- **Status**: `turtle/sensors/temperhum/status`

### Data Format

Each sensor publishes JSON data in this format:
```json
{
  "temperature_c": 29.54,
  "temperature_f": 85.17,
  "humidity": 39.58,
  "interval": 1,
  "timestamp": "2025-08-20T10:30:00Z",
  "unit_of_measurement": {
    "temperature_c": "°C",
    "temperature_f": "°F",
    "humidity": "%"
  }
}
```

### Home Assistant Sensors

The system creates the following sensors in Home Assistant:

- `sensor.turtle_habitat_temperature_1_c` - Temperature in Celsius
- `sensor.turtle_habitat_temperature_1_f` - Temperature in Fahrenheit
- `sensor.turtle_habitat_humidity_1` - Humidity percentage
- `sensor.turtle_habitat_temperature_2_c` - Temperature in Celsius (sensor 2)
- `sensor.turtle_habitat_temperature_2_f` - Temperature in Fahrenheit (sensor 2)
- `sensor.turtle_habitat_humidity_2` - Humidity percentage (sensor 2)
- `sensor.temperhum_manager_status` - Manager status

## Service Management

### Start Service
```bash
sudo systemctl start temperhum-manager.service
```

### Stop Service
```bash
sudo systemctl stop temperhum-manager.service
```

### Restart Service
```bash
sudo systemctl restart temperhum-manager.service
```

### Check Status
```bash
sudo systemctl status temperhum-manager.service
```

### View Logs
```bash
# Real-time logs
sudo journalctl -u temperhum-manager.service -f

# Recent logs
sudo journalctl -u temperhum-manager.service --no-pager -n 50

# Log file
tail -f /var/log/temperhum-manager.log
```

## Testing

### Test Installation
```bash
./setup/test-temperhum-manager.sh
```

### Test Sensor Detection
```bash
python3 -c "
import hid
devices = list(hid.enumerate(0x3553, 0xa001))
print(f'Found {len(devices)} TEMPerHUM device(s)')
for i, device in enumerate(devices):
    print(f'  Device {i+1}: {device}')
"
```

### Test MQTT Data
```bash
# Monitor all TEMPerHUM topics
mosquitto_sub -t 'turtle/sensors/temperhum/#'

# Monitor specific sensor
mosquitto_sub -t 'turtle/sensors/temperhum/sensor_1'
```

### Test Device Access
```bash
python3 -c "
import hid
try:
    device = hid.Device(0x3553, 0xa001)
    print('✅ Device access successful')
    device.close()
except Exception as e:
    print(f'❌ Device access failed: {e}')
"
```

## Troubleshooting

### Common Issues

#### 1. No Sensors Detected
**Symptoms**: Service starts but no sensors are found
**Solutions**:
- Check USB connections
- Verify udev rules are installed
- Check user is in input group
- Reboot or log out/in to apply group changes

#### 2. Permission Denied
**Symptoms**: "Permission denied" errors when accessing devices
**Solutions**:
```bash
# Reinstall udev rules
sudo cp hardware/99-temperhum.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger

# Add user to input group
sudo usermod -a -G input $USER
# Log out and back in
```

#### 3. MQTT Connection Failed
**Symptoms**: Service starts but no MQTT data is published
**Solutions**:
- Check if MQTT broker is running
- Verify MQTT broker is accessible on localhost:1883
- Check firewall settings

#### 4. Sensor Activation Failed
**Symptoms**: Sensors detected but not activated
**Solutions**:
- Check if sensors are already active (try pressing TXT button)
- Verify HID device access
- Check for conflicting processes

#### 5. Data Parsing Errors
**Symptoms**: Raw data received but parsing fails
**Solutions**:
- Check data format matches expected pattern
- Verify sensor is outputting valid data
- Check for data corruption

### Debug Commands

#### Check Device Status
```bash
# List USB devices
lsusb | grep -i temper

# List HID devices
ls /dev/hidraw*

# Check device permissions
ls -la /dev/hidraw*
```

#### Check Service Logs
```bash
# Systemd logs
sudo journalctl -u temperhum-manager.service -f

# Application logs
tail -f /var/log/temperhum-manager.log
```

#### Check MQTT
```bash
# Test MQTT connection
mosquitto_pub -h localhost -t test/topic -m "test message"

# Monitor MQTT topics
mosquitto_sub -t 'turtle/sensors/temperhum/#' -v
```

#### Check Python Dependencies
```bash
python3 -c "import hid; print('pyhidapi OK')"
python3 -c "import paho.mqtt.client; print('paho-mqtt OK')"
```

## Data Validation

### Temperature Range
- **Minimum**: -40.0°C
- **Maximum**: 80.0°C
- **Validation**: Values outside this range are logged as warnings

### Humidity Range
- **Minimum**: 0.0%
- **Maximum**: 100.0%
- **Validation**: Values outside this range are logged as warnings

### Error Handling
- **Max Errors**: 5 consecutive errors before sensor deactivation
- **Recovery**: Service restart reinitializes sensors
- **Logging**: All errors are logged with timestamps

## Performance

### Resource Usage
- **Memory**: ~50MB per sensor
- **CPU**: Minimal (mostly idle)
- **Network**: ~1KB per sensor per 5 seconds

### Reliability
- **Auto-restart**: Service automatically restarts on failure
- **Error recovery**: Sensors are reinitialized on errors
- **Data validation**: All data is validated before publishing

## Security

### Permissions
- **Service user**: shrimp (non-root)
- **Device access**: Input group membership
- **File permissions**: 600 for sensitive files

### Network
- **MQTT**: Localhost only (no external access)
- **Authentication**: None (local network only)

## Monitoring

### Health Checks
```bash
# Check service health
sudo systemctl is-active temperhum-manager.service

# Check sensor data
mosquitto_sub -t 'turtle/sensors/temperhum/#' -C 1

# Check logs for errors
sudo journalctl -u temperhum-manager.service --since "1 hour ago" | grep ERROR
```

### Metrics
- **Sensor count**: Number of active sensors
- **Data rate**: Readings per minute
- **Error rate**: Errors per hour
- **Uptime**: Service uptime

## Support

### Logs Location
- **Systemd logs**: `journalctl -u temperhum-manager.service`
- **Application logs**: `/var/log/temperhum-manager.log`

### Configuration Files
- **Service**: `/etc/systemd/system/temperhum-manager.service`
- **Udev rules**: `/etc/udev/rules.d/99-temperhum.rules`
- **Manager script**: `/home/shrimp/turtle-monitor/hardware/temperhum_manager.py`

### Documentation
- **This file**: `docs/TEMPERHUM-IMPLEMENTATION.md`
- **Installation**: `setup/install-temperhum.sh`
- **Testing**: `setup/test-temperhum-manager.sh`
- **Deployment**: `setup/deploy-temperhum.sh`

---

**🐢 Built for reliable turtle habitat monitoring** 