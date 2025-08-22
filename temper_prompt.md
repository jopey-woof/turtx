[c] 43.65 [%rh] 1s
# TemperhUM USB Sensor Integration - Cursor AI Prompt

## Project Context
I need to integrate two TemperhUM USB sensors into my turtle enclosure monitoring system running on Ubuntu Server 24 with Home Assistant OS in Docker. These sensors behave as HID keyboard devices that "type" temperature and humidity data.

## CRITICAL DEPLOYMENT CONTEXT
**End User**: Non-technical user who will receive this as a complete, working system
**Deployment Goal**: Zero-touch installation and configuration - everything must be automated
**User Expectation**: System works immediately after running setup script, no technical knowledge required

**Development Workflow**:
- **Current Phase**: Local development with sensors connected to dev machine to solve core sensor handling
- **Production Target**: Ubuntu Server 24 with Home Assistant OS in Docker
- **Challenge**: SSH terminal input from HID devices was problematic, hence local development approach
- **Next Phase**: Once sensor data handling is perfected locally, deploy to remote HAOS machine

This means:
- **Develop locally first**: Perfect the sensor initialization, data parsing, and MQTT integration on local machine
- **Test thoroughly**: Ensure reliable HID control and data capture before remote deployment
- **Then deploy remotely**: Transfer working solution to Ubuntu server via automated deployment
- **Complete automation**: No manual Home Assistant configuration steps
- **MQTT auto-discovery**: Sensors must appear automatically in Home Assistant without user intervention
- **Self-configuring**: All MQTT topics, device discovery, and Home Assistant entities created programmatically
- **One-click setup**: Single setup script handles everything from dependencies to service installation
- **Error-proof**: System must be resilient to user mistakes or system changes
- **Documentation**: Simple, non-technical instructions for the end user

## Phased Development Approach
To ensure a logical progression, develop the solution in strict sequential phases. Do not proceed to the next phase until the previous one is fully implemented, tested, and working reliably. Focus on core sensor handling first before any integration or deployment aspects. Each phase should include clear testing steps and debugging output (e.g., live printing of sensor states, commands sent, and data received). **CRITICAL: Phases must not advance prematurely; confirm success criteria with explicit evidence (e.g., logged output showing successful command execution and resulting data).**

**Phase 1: Programmatic Sensor Initialization**
- Focus exclusively on detecting and initializing sensors individually.
- Implement Linux-compatible methods to send HID commands (e.g., Caps Lock hold for 1 second) to toggle each sensor ON/OFF programmatically.
- Detect current state (ON/OFF) by monitoring for output or lack thereof.
- Ensure both sensors can be toggled to ON independently, waiting for and validating banner output.
- **Strict Success Criteria**: Phase 1 is NOT complete until the script can successfully trigger data "typing" from each sensor programmatically (i.e., send toggle command and observe the banner and initial data lines being output without any manual intervention in the final implementation). Display live console output showing: command sent, state before/after, banner received, and sample data lines typed by the sensor. If initial experiments require one-time manual button presses (e.g., pressing Caps Lock once per device) to help debug/learn the exact HID command sequence, that's acceptable for development only—but the final Phase 1 script must achieve fully programmatic control without any manual steps.
- **Do NOT proceed to Phase 2** until programmatic toggling is reliably working for both sensors, with evidence of data output starting/stopping on command.
- Test: Plug in sensors, run initialization script, verify each sensor activates separately with live console output showing command sent, state detection, banner confirmation, and triggered data typing. Iterate on HID methods until this is achieved.
- No parsing, interval adjustment, MQTT, or deployment in this phase.

**Phase 2: Interval Adjustment per Sensor**
- Build on Phase 1: With sensors initialized and ON via programmatic control, implement programmatic double-press commands (Caps Lock to increase, Num Lock to decrease) to set intervals.
- Configure Sensor 1 to 1-second interval (`1S`).
- Configure Sensor 2 to 2-second interval (`2S`).
- Handle cases where current interval is unknown; adjust incrementally as needed.
- Set up a single unified file/stream for both sensors to type into once configured.
- **Strict Success Criteria**: Confirm adjustments by sending commands and observing the interval suffix change in the output data. Live console output must show commands sent, before/after interval values, and sample data lines with the new suffixes.
- Test: After initialization, run adjustment script, verify intervals by monitoring output in the stream with live console printing of raw data lines and confirmed intervals.
- Still no full parsing or integration; just confirm interval suffixes appear correctly.

**Phase 3: Data Parsing and Error Handling**
- Build on Phase 2: With sensors configured and outputting to a unified stream, implement robust parsing.
- Parse each incoming line, extract temperature, humidity, and interval suffix.
- Use interval (`1S` vs `2S`) to identify and route data to sensor-specific structures.
- Handle malformed data, banners, validation, and logging.
- Display live sensor readings: Print each raw input line and parsed values (temperature, humidity, interval, sensor ID) to console for debugging.
- Test: Run full init + adjust + parse script locally, verify parsed data structure with live output; simulate errors to test resilience.
- No MQTT or deployment yet.

**Phase 4: MQTT Integration and Auto-Discovery**
- Build on Phase 3: With reliable parsed data, implement MQTT publishing.
- Set up MQTT broker connection, topics with sensor identification.
- Implement auto-discovery for Home Assistant (programmatic entity creation).
- Include error logging, recovery, and failsafe alerting if sensor control fails.
- Test: Run end-to-end locally (init, adjust, parse, publish), verify data in MQTT and auto-appearance in Home Assistant.

**Phase 5: Automated Deployment and Setup**
- Build on Phase 4: Package the complete solution for remote deployment.
- Create one-click setup script for dependencies, permissions, services.
- Implement systemd service for background operation.
- Develop SSH-based automated deployment script.
- Add repository cleanup, documentation, rollback.
- Test: Deploy to remote Ubuntu server, verify zero-touch operation.

## Sensor Behavior Analysis
**CRITICAL UNDERSTANDING**: These sensors are HID keyboard devices that literally "type" data as keyboard input into whatever has focus (text field, file, terminal). They do NOT communicate via USB protocols - they simulate keyboard typing.

Based on manual testing, the sensors operate as follows:

### Control Mechanism
- **Toggle Data Output**: Press and hold Caps Lock for 1 second to turn output ON/OFF
- **Increase Interval**: Double-press Caps Lock (increases by 1 second increments)  
- **Decrease Interval**: Double-press Num Lock (decreases by 1 second increments)
- **Initial State**: Unknown - sensors could be ON or OFF when system starts

### Data Output Behavior
When activated, each sensor "types" the following into the active text field/file:
1. **Banner text** (one-time on activation)
2. **Continuous data readings** at programmed intervals

**Banner Output (typed as keyboard input):**
```
WWW.PCSENSOR.COM
TEMPERHUM V4.1
CAPS LOCK:ON/OFF/++
NUM LOCK:OFF/ON/-- 
TYPE:INNER-H3
INNER-TEMPINNER-HUMINTERVALWWW.PCSENSOR.COMTEMPERHUMV4.1CAPSLOCK:ON/OFF/++NUMLOCK:OFF/ON/--TYPE:INNER-H3INNER-TEMPINNER-HUMINTERVAL
```

**Continuous Data Format (typed as keyboard input):**
```
29.54[C]39.58[%RH]1S
29.59[C]39.63[%RH]1S
27.60 [C]40.38[%RH]1S
```

### Multi-Sensor Strategy - UPDATED APPROACH
**BREAKTHROUGH SOLUTION**: Use different intervals to identify sensors instead of complex HID device separation.

**Interval-Based Identification Strategy:**
- **Sensor 1**: Configure to 1-second intervals (`1S` in output)
- **Sensor 2**: Configure to 2-second intervals (`2S` in output)  
- **Single unified data stream**: Both sensors type into one file/stream
- **Parse by interval suffix**: Use the `[X]S` identifier to determine which sensor sent each reading

**Why This Works:**
- Eliminates complex HID device routing issues
- No need to separate virtual keyboards or manage multiple file streams
- Natural sensor identification built into the data format
- Much simpler architecture and more reliable operation
- Easy to expand (sensor 3 = 3sec, etc.)

**Sample Data with Identification:**
```
29.54[C]39.58[%RH]1S  ← Sensor 1 data
27.60[C]40.38[%RH]2S  ← Sensor 2 data  
29.51[C]39.55[%RH]1S  ← Sensor 1 data
27.58[C]40.35[%RH]2S  ← Sensor 2 data
```

**Implementation Strategy:**
1. Both sensors type into single monitored file/stream
2. Parse each line and check interval suffix (`1S` vs `2S`)
3. Route parsed data to appropriate sensor topics based on interval
4. No complex device separation required

### Known Issues
- Data output sometimes becomes malformed/out-of-line (observed on Windows)
- Sensors occasionally output unformatted data mixed with valid readings
- Need robust parsing to handle data corruption

## Requirements

### 1. Sensor Communication & Configuration
**CRITICAL REQUIREMENT**: Full programmatic control is essential for turtle life support monitoring - manual button pressing is not acceptable for a living creature's safety.

Create a system that achieves reliable programmatic control on Linux:
- **Primary Goal**: Send Caps Lock hold (1 second) commands programmatically to toggle sensors ON/OFF
- **Secondary Goal**: Send double-press Caps Lock and Num Lock commands to adjust intervals
- Configure Sensor 1 to 1-second intervals using double-press Num Lock (decrease) if needed
- Configure Sensor 2 to 2-second intervals using double-press Caps Lock (increase) if needed  
- Set up single unified file stream for both sensors to type into
- **Linux-specific challenge**: Commands work on Windows but fail on Linux - need Linux-compatible HID input method
- Must work reliably after system boot/power outages for autonomous operation

**Investigation Requirements**:
- Research Linux HID input methods (evdev, hidapi, direct device writing)
- Test different approaches: uinput, /dev/hidraw*, keyboard event injection
- Ensure proper permissions and udev rules for HID device access
- Implement fallback methods if primary approach fails

### 2. Sensor Initialization
Create a robust initialization system that:
- Detects current state of both sensors (ON/OFF)
- Ensures both sensors are toggled to ON state regardless of initial condition
- Handles the case where sensors might already be running
- Waits for and validates the banner output to confirm successful activation

### 3. Data Parsing & Error Handling
Implement resilient data parsing that:
- Correctly extracts temperature and humidity values from the expected format: `XX.XX[C]XX.XX[%RH]XS`
- Gracefully handles malformed data lines
- Filters out banner text that might intermittently appear
- Implements data validation (reasonable temperature/humidity ranges)
- Maintains parsing accuracy even when sensors output corrupted data
- Logs parsing errors for debugging without crashing the application

### 4. Multi-Sensor Management
Handle two sensors simultaneously:
- Distinguish between sensor outputs (if possible via device identification)
- Manage initialization sequence for both devices
- Ensure data from both sensors is properly captured and labeled

### 5. Integration Requirements
- Output parsed data to MQTT for Home Assistant consumption
- Include sensor identification in MQTT topics
- Implement proper error logging and recovery mechanisms
- Create systemd service for automatic startup and recovery

## Technical Specifications
- **Development Platform**: Local machine (for initial sensor handling development)
- **Production Platform**: Ubuntu Server 24.04 with Home Assistant OS in Docker
- **Language**: Python 3 preferred
- **Integration**: MQTT broker for Home Assistant
- **Device Interface**: HID keyboard input capture (local testing, then remote deployment)
- **Service**: Must run as background systemd service on production system
- **SSH Limitation**: HID terminal input over SSH was problematic, requiring local development approach

## IMPORTANT: Fresh Start Required
- **Clean up all previous TemperhUM sensor work** - remove any existing sensor-related code, configurations, and implementations
- **GitHub cleanup**: Remove all previous TemperhUM sensor commits, branches, and related files from the repository
- **Reset development strategy**: Return to our established workflow of remote pulling from GitHub unless absolutely necessary, then using SSH through terminal in an automated fashion for deployments
- **Start completely fresh** using only the specifications and requirements outlined in this prompt

## Deliverables Needed
1. **Repository Cleanup Plan**: Steps to remove all previous TemperhUM sensor code from GitHub (complete before Phase 1)
2. **Linux HID Control Research**: Investigation and implementation of Linux-compatible HID input methods (used in Phases 1-2)
3. **Fresh Implementation**: Complete Python script with programmatic sensor control for Linux, including live printing of parsed sensor readings to the console for debugging purposes (e.g., print each incoming raw line and the parsed temperature/humidity/interval values in real-time during script execution) (built across Phases 1-3)
4. **Robust Data Parsing Module**: With interval-based sensor identification and comprehensive error handling (Phase 3)
5. **MQTT Auto-Discovery Setup**: Automatic Home Assistant sensor creation with zero user configuration (Phase 4)
6. **Complete MQTT Integration**: Full broker setup, topic configuration, and device discovery automation (Phase 4)
7. **One-Click Setup Script**: Single command installation that handles everything (dependencies, permissions, services, MQTT config) (Phase 5)
8. **Systemd Service Configuration**: For reliable background operation and auto-start after power outages (Phase 5)
9. **Automated Deployment Script**: SSH-based deployment that configures everything remotely (Phase 5)
10. **Non-Technical User Documentation**: Simple setup instructions for end user (plug in sensors, run one command) (Phase 5)
11. **Logging and Debugging Capabilities**: Comprehensive monitoring with user-friendly error messages, including optional debug mode in the script to enable live sensor reading display (all phases, enhanced in Phase 3)
12. **Failsafe Alerting**: System to notify if programmatic sensor control fails (critical for turtle safety) (Phase 4-5)

## Development Workflow Requirements
- Clean GitHub repository of all previous TemperhUM attempts
- Implement new solution with clear, documented commits (one phase per major commit/branch if needed)
- **Provide complete automated setup for non-technical end user**
- Create one-command installation script that handles everything
- Include automated SSH deployment script for remote installation
- Maintain our established pattern of minimal local development, maximum remote repository utilization
- Include rollback capabilities in case of deployment issues
- **End user should only need to: plug in sensors, run setup script, done**

## Sample Data Structure Expected
```python
# Parsed from unified stream using interval identification
{
    "sensor_1": {  # Identified by "1S" suffix
        "temperature": 29.54,
        "humidity": 39.58,
        "timestamp": "2025-08-20T10:30:00Z",
        "interval": 1,
        "last_seen": "2025-08-20T10:30:00Z"
    },
    "sensor_2": {  # Identified by "2S" suffix  
        "temperature": 27.60,
        "humidity": 40.38,
        "timestamp": "2025-08-20T10:30:01Z", 
        "interval": 2,
        "last_seen": "2025-08-20T10:30:01Z"
    }
}
```

## Key Implementation Notes
- **CRITICAL**: This is life support monitoring for a living turtle - manual intervention is not acceptable
- **Linux HID Challenge**: Need to solve programmatic HID input on Linux (works on Windows, fails on Linux)
- **Autonomous Operation**: Must work reliably after power outages and system reboots
- **Much simpler architecture**: Single file stream eliminates HID device separation complexity
- **Natural sensor identification**: Built into the data format via interval suffixes (`1S` vs `2S`)
- **Reliable differentiation**: Different intervals prevent sensor confusion and reduce output conflicts
- **Expandable**: Additional sensors can use 3S, 4S, etc.
- **Failsafe Required**: Alert mechanism if automated sensor control fails
- **Debugging Enhancement**: The main Python script must include code to display live sensor readings (raw input and parsed data) to stdout for debugging during development and testing; this can be toggled via a command-line flag or config option for production use
- **Phased Strictness**: Do not develop MQTT or deployment until sensor init, adjustment, and parsing are perfected and tested locally. Specifically, do not leave Phase 1 without confirmed programmatic triggering of data output.

**Potential Linux HID Solutions to Investigate**:
- evdev library for direct device input
- hidapi for cross-platform HID communication  
- Writing directly to /dev/hidraw* devices
- uinput for kernel-level input event injection
- Different permission/udev rule configurations

Please create a complete, production-ready solution that handles all edge cases and provides reliable sensor data for my turtle enclosure monitoring system.[%rh]   1s
