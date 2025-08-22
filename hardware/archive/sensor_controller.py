import hid
import time
import re
import threading
from queue import Queue
import evdev
import os

# USB HID Keycode to ASCII mapping (simplified for this device)
# Using evdev keycodes now
KEYCODE_MAP = {
    0x1E: '1', 0x1F: '2', 0x20: '3', 0x21: '4', 0x22: '5',
    0x23: '6', 0x24: '7', 0x25: '8', 0x26: '9', 0x27: '0',
    0x37: '.', 0x2D: '[', 0x2E: ']', 0x06: 'C', 0x0B: 'H',
    0x15: 'R', 0x16: 'S', 0x38: '%',
    0x28: '\n' # Enter key
}

class Sensor:
    """Represents a single TemperhUM sensor."""
    def __init__(self, name, paths):
        self.name = name
        self.hid_paths = paths
        self.evdev_device = None # To hold the evdev input device
        self.target_interval = None

def print_device_details():
    """Prints detailed information for all evdev input devices."""
    print("\n--- EVDEV DEVICE DETAILS ---")
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        print(f"Path: {device.path}, Name: {device.name}, Phys: {device.phys}")
        uevent_path = f"/sys/class/input/{os.path.basename(device.path)}/device/uevent"
        if os.path.exists(uevent_path):
            with open(uevent_path, 'r') as f:
                print(f"  {f.read().strip()}")
        print("-" * 20)

def find_sensor_devices():
    """Finds all TemperhUM sensor devices for command sending (hidapi)."""
    devices = hid.enumerate()
    sensor_interfaces = []
    for device in devices:
        if device['vendor_id'] == 0x3553 and device['product_id'] == 0xa001:
            sensor_interfaces.append(device)
    
    # Group interfaces by physical device (based on USB path)
    grouped_sensors = {}
    for interface in sensor_interfaces:
        # The base path is the part before the final interface number (e.g., '1-1' from '1-1:1.0')
        base_path = interface['path'].decode().split(':')[0]
        if base_path not in grouped_sensors:
            grouped_sensors[base_path] = []
        grouped_sensors[base_path].append(interface['path'])

    # Create Sensor objects from hidapi paths
    sensors = []
    for i, (base_path, paths) in enumerate(grouped_sensors.items()):
        sensors.append(Sensor(f"Sensor-{i+1}", paths))

    return sensors

def find_keyboard_devices():
    """Finds all evdev keyboard devices for data reading."""
    keyboards = []
    evdev_devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in evdev_devices:
        if "TEMPerHUM" in device.name:
            keyboards.append(device)
    return keyboards

def send_command(device_path, command):
    """Sends a command to a specific sensor."""
    try:
        device = hid.device()
        device.open_path(device_path)
        device.write(command)
        device.close()
    except Exception as e:
        print(f"Error sending command to {device_path.decode()}: {e}")

def get_toggle_command(pressed=True):
    """Returns the command to toggle the sensor (Caps Lock)."""
    if pressed:
        return [0x00, 0x02, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00]
    else:
        return [0x00] * 8

def get_increase_interval_command(pressed=True):
    """Returns the command to increase the interval (Caps Lock)."""
    return get_toggle_command(pressed)

def get_decrease_interval_command(pressed=True):
    """Returns the command to decrease the interval (Num Lock)."""
    if pressed:
        # Num Lock keycode is 0x53
        return [0x00, 0x00, 0x00, 0x53, 0x00, 0x00, 0x00, 0x00]
    else:
        return [0x00] * 8

def configure_sensor(sensor, target_interval):
    """Configures a sensor to the target interval."""
    print(f"\nConfiguring {sensor.name} to {target_interval}s interval...")
    sensor.target_interval = target_interval
    
    # For now, we assume we need to increase the interval.
    # A more robust implementation would read the current interval first.
    if target_interval > 1:
        for _ in range(target_interval - 1):
            print(f"  - Increasing interval for {sensor.name}")
            for path in sensor.hid_paths:
                send_command(path, get_increase_interval_command(pressed=True))
                send_command(path, get_increase_interval_command(pressed=False))
                time.sleep(0.1)
                send_command(path, get_increase_interval_command(pressed=True))
                send_command(path, get_increase_interval_command(pressed=False))
    
    # Always toggle the sensor on to ensure it's outputting data
    print(f"  - Toggling {sensor.name} ON")
    for path in sensor.hid_paths:
        send_command(path, get_toggle_command(pressed=True))
        time.sleep(1)
        send_command(path, get_toggle_command(pressed=False))
    print(f"{sensor.name} configured.")

def listener(device, queue):
    """Listens for input events from a device and puts keycodes in a queue."""
    try:
        for event in device.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                key_event = evdev.categorize(event)
                if key_event.keystate == key_event.key_down:
                    queue.put(key_event.scancode)
    except Exception as e:
        print(f"Device listener error for {device.path}: {e}. Thread stopping.")

def processor(queue):
    """Processes keycodes from the queue, forms lines, and parses them."""
    line_buffer = ""
    while True:
        keycode = queue.get()
        char = KEYCODE_MAP.get(keycode)
        if char:
            if char == '\n':
                if line_buffer:
                    parse_line(line_buffer)
                line_buffer = ""
            else:
                line_buffer += char

def parse_line(line):
    """Parses a single line of sensor data."""
    print(f"Raw data: {line}")
    match = re.match(r"(\d+\.\d+)\s*\[C\]\s*(\d+\.\d+)\s*\[%RH\]\s*(\d+)S", line)
    if match:
        temp = float(match.group(1))
        humidity = float(match.group(2))
        interval = int(match.group(3))
        sensor_id = f"Sensor-{interval}"
        
        print(f"  -> Parsed: Sensor={sensor_id}, Temp={temp}°C, Humidity={humidity}%")
    else:
        print("  -> Failed to parse line.")

def main():
    """Main function to find and test sensors."""
    command_sensors = find_sensor_devices()
    keyboard_sensors = find_keyboard_devices()

    if not command_sensors:
        print("No TemperhUM command interfaces found.")
        return
    if not keyboard_sensors:
        print("No TemperhUM keyboard interfaces found.")
        return

    # Configure each sensor
    if len(command_sensors) > 0:
        configure_sensor(command_sensors[0], 1)
    if len(command_sensors) > 1:
        configure_sensor(command_sensors[1], 2)

    # Start listener threads for all keyboard interfaces
    print("\nStarting sensor listeners...")
    data_queue = Queue()
    
    for keyboard in keyboard_sensors:
        thread = threading.Thread(target=listener, args=(keyboard, data_queue), daemon=True)
        thread.start()
        print(f"  - Listener started for {keyboard.path}")

    # Start the processor thread
    proc_thread = threading.Thread(target=processor, args=(data_queue,), daemon=True)
    proc_thread.start()
    print("Data processor started.")

    # Keep the main thread alive
    print("\n--- REAL-TIME SENSOR DATA ---")
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()