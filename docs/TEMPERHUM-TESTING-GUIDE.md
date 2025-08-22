# TEMPerHUM USB Sensor Testing Guide

## Overview

This guide provides step-by-step instructions for testing TEMPerHUM USB temperature/humidity sensors on your remote Linux machine. The testing process is interactive and guides you through each step to ensure proper sensor functionality.

## Prerequisites

- SSH access to remote machine (shrimp@10.0.20.69)
- TEMPerHUM USB sensors (2 sensors recommended)
- USB ports available on remote machine
- Python 3.6+ on remote machine

## Quick Start

### Option 1: Automated Deployment (Recommended)

```bash
# From your local machine
chmod +x setup/deploy-temperhum-test.sh
./setup/deploy-temperhum-test.sh
```

This will:
1. Copy the test script to the remote machine
2. Install dependencies automatically
3. Run the interactive test process
4. Save results for review

### Option 2: Manual Execution

```bash
# SSH to remote machine
ssh shrimp@10.0.20.69

# Navigate to project directory
cd /home/shrimp/turtle-monitor

# Run the test script
python3 hardware/temperhum_test_installer.py
```

## Test Process Overview

The test script performs the following steps:

1. **Environment Check**
   - Verify Python version (3.6+)
   - Check system dependencies

2. **Dependency Installation**
   - Install system packages (python3-pip, python3-serial, etc.)
   - Install temper-py Python package
   - Configure device permissions

3. **Device Detection**
   - Scan USB devices for TEMPerHUM sensors
   - Detect HID devices
   - Identify sensor vendor/product IDs

4. **Sensor Testing**
   - Test each sensor individually
   - Attempt programmatic reading via temper-py
   - Fallback to manual activation mode if needed
   - Parse temperature and humidity data

5. **Results Collection**
   - Save test results to JSON files
   - Provide troubleshooting guidance
   - Generate summary report

## Interactive Testing Steps

### Step 1: Environment Setup

The script will automatically:
- Check Python version compatibility
- Install required system packages
- Install temper-py Python package
- Test basic functionality

### Step 2: Device Detection

The script will scan for TEMPerHUM sensors using:
- `lsusb` command to detect USB devices
- HID device enumeration
- Known vendor/product ID matching

**Expected Output:**
```
→ Detecting USB devices...
✓ TEMPerHUM sensor detected: Bus 001 Device 003: ID 413d:2107 TEMPerHUM
→ Detecting HID devices...
✓ HID device detected: hidraw0
```

### Step 3: Sensor Testing

For each sensor, the script will:

1. **Prompt for Connection**
   ```
   Step 1: Verify sensor connection
   Please ensure sensor 1 is plugged into a USB port, then press Enter...
   ```

2. **Attempt Programmatic Reading**
   - Try temper-py CLI commands
   - Parse temperature and humidity data
   - Display results

3. **Manual Mode (if needed)**
   - Guide you through button activation
   - Capture typed output
   - Parse sensor data

### Step 4: Results Review

The script will display:
- Test success/failure status
- Temperature and humidity readings
- Method used (programmatic or manual)
- Troubleshooting suggestions

## Expected Sensor Output Formats

TEMPerHUM sensors can output data in several formats:

### Format 1: Standard TEMPerHUM
```
32.73[C]36.82[%RH]1S
```

### Format 2: Temperature and Humidity
```
32.73°C 36.82%
```

### Format 3: Descriptive Format
```
Temp: 32.73°C, Humidity: 36.82%
```

## Troubleshooting

### Common Issues and Solutions

#### 1. No Sensors Detected

**Symptoms:**
- `lsusb` shows no TEMPerHUM devices
- HID device detection fails

**Solutions:**
```bash
# Check USB devices
ssh shrimp@10.0.20.69 'lsusb'

# Check system logs
ssh shrimp@10.0.20.69 'dmesg | tail -20'

# Verify sensor is powered (LED should be on)
# Try different USB port
# Check if sensor is in special mode
```

#### 2. temper-py Installation Fails

**Symptoms:**
- pip install temper-py fails
- Import errors

**Solutions:**
```bash
# Manual installation
ssh shrimp@10.0.20.69 'pip3 install --user temper-py'

# Alternative installation
ssh shrimp@10.0.20.69 'python3 -m pip install temper-py'

# Check Python environment
ssh shrimp@10.0.20.69 'python3 --version && pip3 --version'
```

#### 3. Permission Denied Errors

**Symptoms:**
- Cannot access /dev/hidraw*
- Permission denied on device files

**Solutions:**
```bash
# Add user to input group
ssh shrimp@10.0.20.69 'sudo usermod -a -G input shrimp'

# Check udev rules
ssh shrimp@10.0.20.69 'ls -la /etc/udev/rules.d/99-temperhum.rules'

# Reload udev rules
ssh shrimp@10.0.20.69 'sudo udevadm control --reload-rules'
```

#### 4. No Data from Sensors

**Symptoms:**
- Sensors detected but no readings
- Programmatic reading fails

**Solutions:**
```bash
# Test manual activation
ssh shrimp@10.0.20.69 'python3 /tmp/temperhum_capture.py'

# Check sensor mode
# Press TXT button on sensor
# Hold Caps Lock for 3 seconds

# Verify sensor is not in special mode
# Unplug and replug sensor
```

#### 5. Invalid or Corrupted Data

**Symptoms:**
- Readings outside expected ranges
- Malformed data strings

**Solutions:**
```bash
# Check raw sensor output
ssh shrimp@10.0.20.69 'cat /tmp/temperhum_captured_data.json'

# Verify sensor calibration
# Check for interference
# Test in different environment
```

## Manual Testing Commands

If the automated script fails, you can test manually:

### 1. Check USB Devices
```bash
ssh shrimp@10.0.20.69 'lsusb | grep -i temperhum'
```

### 2. Test temper-py
```bash
ssh shrimp@10.0.20.69 'temper.py --help'
ssh shrimp@10.0.20.69 'temper.py'
```

### 3. Manual Capture Test
```bash
ssh shrimp@10.0.20.69 'python3 /tmp/temperhum_capture.py'
```

### 4. Check System Logs
```bash
ssh shrimp@10.0.20.69 'dmesg | grep -i usb'
ssh shrimp@10.0.20.69 'journalctl -f'
```

## Expected Results

### Successful Test Output

```
============================================================
  Test Summary
============================================================

✓ Successfully tested 2 sensors
ℹ Sensor 1: temper-py method
  Temperature: 24.5°C
  Humidity: 45.2%
ℹ Sensor 2: manual method
  Temperature: 24.3°C
  Humidity: 44.8%
✓ Test results saved to /tmp/temperhum_test_results_20250120_143022.json
```

### Test Results File

Results are saved in JSON format:
```json
[
  {
    "sensor_id": 1,
    "method": "temper-py",
    "temperature": 24.5,
    "humidity": 45.2,
    "raw_output": "24.5°C 45.2%",
    "timestamp": "2025-01-20T14:30:22.123456"
  },
  {
    "sensor_id": 2,
    "method": "manual",
    "temperature": 24.3,
    "humidity": 44.8,
    "raw_data": "24.3[C]44.8[%RH]1S",
    "timestamp": "2025-01-20T14:31:15.654321"
  }
]
```

## Next Steps After Successful Testing

1. **Integration with Home Assistant**
   - Configure MQTT sensors
   - Set up automations
   - Create dashboard widgets

2. **Production Deployment**
   - Set up systemd service
   - Configure logging
   - Implement monitoring

3. **Data Analysis**
   - Review historical data
   - Set up alerts
   - Configure data retention

## Support and Resources

### Documentation
- [TEMPerHUM Implementation Guide](TEMPERHUM-IMPLEMENTATION.md)
- [Hardware Setup Notes](HARDWARE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

### External Resources
- [TEMPerHUM Documentation](https://cdn.pcsensor.com/wp-content/uploads/2025/04/TEMPerHUM%E8%B6%85%E9%95%BF%E8%8B%B1%E6%96%87%E8%AF%B4%E6%98%8E%E4%B9%A6_EN_V6.pdf)
- [temper-py Package](https://pypi.org/project/temper-py/)
- [HID-TEMPerHUM GitHub](https://github.com/jeixav/HID-TEMPerHUM)

### Monitoring Commands
```bash
# Check service status
ssh shrimp@10.0.20.69 'sudo systemctl status temperhum-manager.service'

# View live logs
ssh shrimp@10.0.20.69 'sudo journalctl -u temperhum-manager.service -f'

# Monitor MQTT data
ssh shrimp@10.0.20.69 'mosquitto_sub -t "turtle/sensors/temperhum/#" -v'
```

---

**🐢 Built with care for our shelled friends**

This testing guide ensures reliable sensor operation for the eastern box turtle monitoring system. 