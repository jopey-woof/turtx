#!/usr/bin/env python3
"""
Quick TEMPerHUM Capture Test
============================

Simple script to capture existing keyboard input from TEMPerHUM sensors
with proper timeouts - no activation needed.
"""

import evdev
import time
import sys
import signal

def signal_handler(signum, frame):
    print("\n⏰ Timeout reached, exiting...")
    sys.exit(0)

def find_temperhum_devices():
    """Find TEMPerHUM devices"""
    devices = []
    for path in evdev.list_devices():
        try:
            device = evdev.InputDevice(path)
            if 'temperhum' in device.name.lower() or 'pcsensor' in device.name.lower():
                print(f"Found TEMPerHUM device: {device.name} at {path}")
                devices.append(device)
        except:
            continue
    return devices

def keycode_to_char(keycode):
    """Convert keycode to character"""
    key_map = {
        'KEY_A': 'a', 'KEY_B': 'b', 'KEY_C': 'c', 'KEY_D': 'd', 'KEY_E': 'e',
        'KEY_F': 'f', 'KEY_G': 'g', 'KEY_H': 'h', 'KEY_I': 'i', 'KEY_J': 'j',
        'KEY_K': 'k', 'KEY_L': 'l', 'KEY_M': 'm', 'KEY_N': 'n', 'KEY_O': 'o',
        'KEY_P': 'p', 'KEY_Q': 'q', 'KEY_R': 'r', 'KEY_S': 's', 'KEY_T': 't',
        'KEY_U': 'u', 'KEY_V': 'v', 'KEY_W': 'w', 'KEY_X': 'x', 'KEY_Y': 'y',
        'KEY_Z': 'z',
        'KEY_0': '0', 'KEY_1': '1', 'KEY_2': '2', 'KEY_3': '3', 'KEY_4': '4',
        'KEY_5': '5', 'KEY_6': '6', 'KEY_7': '7', 'KEY_8': '8', 'KEY_9': '9',
        'KEY_DOT': '.', 'KEY_SPACE': ' ', 'KEY_ENTER': '\n',
        'KEY_LEFTBRACE': '[', 'KEY_RIGHTBRACE': ']',
        'KEY_SEMICOLON': ';', 'KEY_APOSTROPHE': "'",
        'KEY_COMMA': ',', 'KEY_SLASH': '/', 'KEY_BACKSLASH': '\\',
        'KEY_MINUS': '-', 'KEY_EQUAL': '=', 'KEY_PERCENT': '%'
    }
    
    if isinstance(keycode, list):
        keycode = keycode[0]
    
    return key_map.get(keycode, '')

def quick_capture(device, sensor_id, timeout=10):
    """Quick capture with timeout"""
    print(f"\n🧪 Quick capture from {sensor_id}: {device.name}")
    print(f"⏰ Timeout: {timeout} seconds")
    print("=" * 50)
    
    captured_text = ""
    start_time = time.time()
    
    try:
        # Set a signal timeout
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(timeout)
        
        # Grab the device to capture its events
        device.grab()
        
        while time.time() - start_time < timeout:
            try:
                for event in device.read_loop():
                    if time.time() - start_time > timeout:
                        break
                        
                    if event.type == evdev.ecodes.EV_KEY and event.value == 1:  # Key press
                        try:
                            key_event = evdev.categorize(event)
                            if hasattr(key_event, 'keycode'):
                                keycode = key_event.keycode
                                
                                # Convert keycode to character
                                char = keycode_to_char(keycode)
                                if char:
                                    captured_text += char
                                    print(f"📝 Captured: '{char}' (total: {len(captured_text)} chars)")
                                    
                        except Exception as e:
                            print(f"Error processing event: {e}")
                            
            except BlockingIOError:
                # No events available
                time.sleep(0.1)
                continue
            except Exception as e:
                print(f"Error reading events: {e}")
                break
                
    except Exception as e:
        print(f"❌ Error capturing data: {e}")
    finally:
        try:
            signal.alarm(0)  # Cancel the alarm
            device.ungrab()
        except:
            pass
    
    # Display results
    print("\n3️⃣ Results:")
    print("=" * 30)
    if captured_text:
        print(f"✅ Captured {len(captured_text)} characters:")
        print(f"📄 Raw data: {repr(captured_text)}")
        print(f"📄 Text: {captured_text}")
        
        # Look for specific patterns
        if "WWW.PCSENSOR.COM" in captured_text:
            print("🎉 Found banner: WWW.PCSENSOR.COM")
        if "TEMPERHUM" in captured_text:
            print("🎉 Found TEMPERHUM identifier")
        if "[C]" in captured_text and "[%RH]" in captured_text:
            print("🌡️  Found temperature/humidity data!")
    else:
        print("❌ No data captured")
        print("💡 Sensors may not be typing or may need manual activation")

def main():
    print("🐢 TEMPerHUM Quick Capture Test")
    print("=" * 40)
    
    # Find devices
    devices = find_temperhum_devices()
    
    if not devices:
        print("❌ No TEMPerHUM devices found!")
        return
    
    print(f"✅ Found {len(devices)} TEMPerHUM device(s)")
    
    # Test each device with 10-second timeout
    for i, device in enumerate(devices):
        quick_capture(device, f"sensor_{i+1}", timeout=10)
        
        if i < len(devices) - 1:
            print("\n" + "="*60 + "\n")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    main() 