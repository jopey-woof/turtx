# TemperhUM USB Sensor Integration Guide

## Overview

This guide covers the complete setup and operation of TemperhUM USB temperature and humidity sensors for turtle enclosure monitoring. The system uses two sensors configured with different intervals to distinguish between them automatically.

## System Architecture

### Sensor Configuration Strategy
- **Sensor 1**: Configured to 1-second intervals (`1S` in output)
- **Sensor 2**: Configured to 2-second intervals (`2S` in output)
- **Data Stream**: Both sensors type into a single monitored file
- **Identification**: Sensors are identified by the interval suffix in their data output

### Data Flow
1. Sensors type data into `/tmp/temperhum_data.txt`
2. Python script monitors the file for new data
3. Data is parsed and identified by interval
4. Parsed data is published to MQTT
5. Home Assistant auto-discovers sensors via MQTT

## Prerequisites

### Hardware Requirements
- 2x TemperhUM V4.1 USB sensors
- Ubuntu Server 24.04 or later
- USB ports for sensor connection

### Software Requirements
- Python 3.8+
- MQTT broker (mosquitto)
- Home Assistant (for monitoring)

## Installation

### One-Click Installation (Recommended)

For end users, simply run:

```bash
# On the remote Ubuntu server
cd /home/shrimp/turtle-monitor
./setup/install-temperhum.sh
```

This script will:
- Install all required dependencies
- Configure udev rules for device access
- Setup MQTT broker
- Install and start the data capture service
- Configure auto-discovery for Home Assistant

### Manual Installation

If you prefer manual installation:

1. **Install Python dependencies:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-pip python3-dev python3-evdev
   pip3 install --user paho-mqtt evdev python-evdev
   ```

2. **Setup udev rules:**
   ```bash
   sudo cp hardware/99-temperhum-sensors.rules /etc/udev/rules.d/
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

3. **Install MQTT broker:**
   ```bash
   sudo apt-get install -y mosquitto mosquitto-clients
   sudo systemctl enable mosquitto
   sudo systemctl start mosquitto
   ```

4. **Install systemd service:**
   ```bash
   sudo cp hardware/temperhum-capture.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable temperhum-capture.service
   sudo systemctl start temperhum-capture.service
   ```

## Sensor Configuration

### Manual Sensor Setup

1. **Plug in both sensors** to USB ports

2. **Configure Sensor 1 (1-second intervals):**
   - Hold Caps Lock for 1 second to toggle ON
   - If needed, double-press Num Lock to decrease interval to 1 second
   - Verify output shows `1S` suffix

3. **Configure Sensor 2 (2-second intervals):**
   - Hold Caps Lock for 1 second to toggle ON
   - Double-press Caps Lock to increase interval to 2 seconds
   - Verify output shows `2S` suffix

### Sensor Control Commands

| Action | Command |
|--------|---------|
| Toggle ON/OFF | Hold Caps Lock for 1 second |
| Increase interval | Double-press Caps Lock |
| Decrease interval | Double-press Num Lock |

### Expected Data Format

**Banner Output (one-time):**
```
WWW.PCSENSOR.COM
TEMPERHUM V4.1
CAPS LOCK:ON/OFF/++
NUM LOCK:OFF/ON/-- 
TYPE:INNER-H3
```

**Continuous Data:**
```
29.54[C]39.58[%RH]1S  ← Sensor 1 (1-second intervals)
27.60[C]40.38[%RH]2S  ← Sensor 2 (2-second intervals)
```

## Operation

### Starting the System

The system starts automatically after installation. To manually control:

```bash
# Start the service
sudo systemctl start temperhum-capture.service

# Check status
sudo systemctl status temperhum-capture.service

# View logs
tail -f /var/log/temperhum-capture.log
```

### Monitoring Data

**View live sensor data:**
```bash
tail -f /tmp/temperhum_data.txt
```

**Check sensor status:**
```bash
# The service prints status every 5 seconds in debug mode
sudo systemctl restart temperhum-capture.service
```

**View MQTT messages:**
```bash
mosquitto_sub -t "turtle/sensors/temperhum/#" -v
```

### Home Assistant Integration

Sensors are automatically discovered in Home Assistant via MQTT auto-discovery:

**Entity Names:**
- `sensor.turtle_sensor_1_temperature`
- `sensor.turtle_sensor_1_humidity`
- `sensor.turtle_sensor_2_temperature`
- `sensor.turtle_sensor_2_humidity`

**MQTT Topics:**
- `turtle/sensors/temperhum/sensor_1/temperature`
- `turtle/sensors/temperhum/sensor_1/humidity`
- `turtle/sensors/temperhum/sensor_2/temperature`
- `turtle/sensors/temperhum/sensor_2/humidity`

## Troubleshooting

### Common Issues

**1. Sensors not detected:**
```bash
# Check USB devices
lsusb

# Check input devices
ls /dev/input/

# Check udev rules
sudo udevadm test /sys/class/input/event*
```

**2. Permission errors:**
```bash
# Add user to input group
sudo usermod -a -G input $USER

# Check device permissions
ls -la /dev/input/
```

**3. Service not starting:**
```bash
# Check service logs
sudo journalctl -u temperhum-capture.service -f

# Check dependencies
sudo systemctl status mosquitto
```

**4. No data appearing:**
```bash
# Check if sensors are typing data
tail -f /tmp/temperhum_data.txt

# Test manual data entry
echo "29.54[C]39.58[%RH]1S" >> /tmp/temperhum_data.txt
```

**5. MQTT connection issues:**
```bash
# Test MQTT connectivity
mosquitto_pub -t "test/topic" -m "test message"
mosquitto_sub -t "test/topic" -C 1
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Stop the service
sudo systemctl stop temperhum-capture.service

# Run manually with debug
cd /home/shrimp/turtle-monitor/hardware
python3 simple_data_capture.py --debug
```

### Data Validation

The system validates sensor data with these ranges:
- **Temperature**: 0-50°C
- **Humidity**: 0-100%RH
- **Interval**: Must match configured intervals (1S or 2S)

Invalid data is logged and ignored.

## Maintenance

### Log Rotation

Logs are stored in `/var/log/temperhum-capture.log`. Consider setting up log rotation:

```bash
sudo tee /etc/logrotate.d/temperhum-capture > /dev/null <<EOF
/var/log/temperhum-capture.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 shrimp shrimp
}
EOF
```

### Data Backup

The data file `/tmp/temperhum_data.txt` is temporary. For long-term storage, consider:

```bash
# Create backup script
sudo tee /usr/local/bin/backup-temperhum-data.sh > /dev/null <<'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /tmp/temperhum_data.txt /home/shrimp/backups/temperhum_data_$DATE.txt
EOF

sudo chmod +x /usr/local/bin/backup-temperhum-data.sh

# Add to crontab
echo "0 */6 * * * /usr/local/bin/backup-temperhum-data.sh" | crontab -
```

### Service Updates

To update the service:

```bash
# Stop service
sudo systemctl stop temperhum-capture.service

# Update files
cd /home/shrimp/turtle-monitor
git pull

# Restart service
sudo systemctl start temperhum-capture.service
```

## Security Considerations

### Network Security
- MQTT broker is configured for local access only
- Consider adding authentication for production use
- Firewall rules should restrict MQTT port access

### Device Security
- udev rules grant broad access to input devices
- Consider more restrictive rules for production
- Regular security updates for Ubuntu system

### Data Privacy
- Sensor data is stored locally
- MQTT messages are not encrypted by default
- Consider TLS for MQTT in sensitive environments

## Support

### Getting Help

1. **Check logs first:**
   ```bash
   tail -f /var/log/temperhum-capture.log
   ```

2. **Run diagnostic tests:**
   ```bash
   cd /home/shrimp/turtle-monitor/hardware
   python3 test-temperhum-local.py
   ```

3. **Verify system status:**
   ```bash
   sudo systemctl status temperhum-capture.service
   sudo systemctl status mosquitto
   ```

### Common Commands Reference

| Command | Purpose |
|---------|---------|
| `sudo systemctl status temperhum-capture.service` | Check service status |
| `sudo systemctl restart temperhum-capture.service` | Restart service |
| `tail -f /var/log/temperhum-capture.log` | View live logs |
| `tail -f /tmp/temperhum_data.txt` | View sensor data |
| `mosquitto_sub -t "turtle/sensors/temperhum/#" -v` | Monitor MQTT messages |
| `lsusb` | List USB devices |
| `ls /dev/input/` | List input devices |

## License

This project is part of the Turtle Monitoring System and follows the same licensing terms. 