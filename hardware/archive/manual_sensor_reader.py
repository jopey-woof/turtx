import evdev
import asyncio

# A simplified map for the characters these sensors output
KEYCODE_MAP = {
    'KEY_1': '1', 'KEY_2': '2', 'KEY_3': '3', 'KEY_4': '4', 'KEY_5': '5',
    'KEY_6': '6', 'KEY_7': '7', 'KEY_8': '8', 'KEY_9': '9', 'KEY_0': '0',
    'KEY_DOT': '.', 'KEY_LEFTBRACE': '[', 'KEY_RIGHTBRACE': ']', 'KEY_C': 'C',
    'KEY_H': 'H', 'KEY_R': 'R', 'KEY_S': 'S', 'KEY_5': '%', # This is likely shift+5
    'KEY_ENTER': '\n', 'KEY_SPACE': ' '
}

async def print_events(device):
    """Reads events from a device and prints the character equivalent."""
    print(f"Listening for events on {device.path} ({device.name})...")
    try:
        async for event in device.async_read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                key_event = evdev.categorize(event)
                if key_event.keystate == key_event.key_down:
                    char = KEYCODE_MAP.get(key_event.keycode)
                    if char == '\n':
                        print() # Newline
                    elif char:
                        print(char, end='', flush=True)
    except OSError as e:
        print(f"\nError reading from {device.path}: {e}. The device may have been disconnected.")
    except Exception as e:
        print(f"\nAn unexpected error occurred with {device.path}: {e}")

async def main():
    """Finds all TemperHUM devices and starts a listener for each."""
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    temperhum_devices = [d for d in devices if "TEMPerHUM" in d.name]

    if not temperhum_devices:
        print("No TemperhUM devices found. Please ensure they are connected and you have the correct permissions.")
        print("Try running with 'sudo'.")
        return

    print("Found TemperhUM devices. Please manually press/hold Caps Lock to activate a sensor.")
    tasks = [print_events(device) for device in temperhum_devices]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting.")