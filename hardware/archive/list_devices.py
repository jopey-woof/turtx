import evdev
import sys
import os
import subprocess

def get_udev_info(device_path):
    """Fetches udev information for a given device path."""
    udev_info = {}
    try:
        # udevadm info -q property -p /sys/class/input/eventX/device
        # For evdev devices, the sysfs path is usually /sys/class/input/eventN
        # We need the parent device path for USB information
        sysfs_path_base = f"/sys/class/input/{os.path.basename(device_path)}"
        device_sysfs_path = os.path.realpath(os.path.join(sysfs_path_base, 'device'))

        # Run udevadm info and parse relevant properties
        cmd = ['udevadm', 'info', '-q', 'property', '-p', device_sysfs_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        for line in result.stdout.splitlines():
            if '=' in line:
                key, value = line.split('=', 1)
                udev_info[key] = value

        # Also try to get info from the parent USB device if applicable
        # Traverse up the sysfs path to find the USB device itself
        current_path = device_sysfs_path
        while current_path != '/' and 'usb' not in os.path.basename(current_path).lower():
            parent_path = os.path.dirname(current_path)
            if parent_path == current_path: # Prevent infinite loop at root
                break
            current_path = parent_path
        
        if 'usb' in os.path.basename(current_path).lower():
            cmd_usb = ['udevadm', 'info', '-q', 'property', '-p', current_path]
            result_usb = subprocess.run(cmd_usb, capture_output=True, text=True, check=True)
            for line in result_usb.stdout.splitlines():
                if '=' in line:
                    key, value = line.split('=', 1)
                    udev_info[key] = value


    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        # print(f"Warning: Could not get udevadm info for {device_path}: {e}") # Too noisy
        pass
    return udev_info

def list_evdev_devices():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    if not devices:
        print("No evdev input devices found.")
        return

    print("\n--- Available evdev input devices and their properties ---")
    for device in devices:
        print(f"Device Path: {device.path}")
        print(f"  Name: {device.name}")
        print(f"  Phys: {device.phys}")
        print(f"  Uniq: {device.uniq}")
        print(f"  Bus: {device.info.bustype} (0x{device.info.bustype:04x})")
        print(f"  Vendor ID: {device.info.vendor} (0x{device.info.vendor:04x})")
        print(f"  Product ID: {device.info.product} (0x{device.info.product:04x})")
        print(f"  Version: {device.info.version} (0x{device.info.version:04x})")

        udev_info = get_udev_info(device.path)
        if udev_info:
            print("  udevadm Info:")
            for key, value in udev_info.items():
                print(f"    {key}: {value}")

        print("  Capabilities (verbose):")
        for type, codes in device.capabilities(verbose=True).items():
            print(f"    Type {type[0]} ({type[1]}):")
            for code in codes:
                if len(code) == 3:
                    print(f"      {code[0]} ({code[1]}) - {code[2]}")
                else:
                    print(f"      {code[0]} ({code[1]}) - No description")
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    list_evdev_devices()