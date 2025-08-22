#!/usr/bin/env python3
"""
Text Output Monitor - Monitor for sensor text output when control commands work
"""
import os
import time
import evdev
import threading
import queue
from temperhum_controller import TemperhUMController

class TextOutputMonitor:
    def __init__(self):
        self.controller = TemperhUMController(verbose=True)
        self.text_queue = queue.Queue()
        self.monitoring = False
        
    def find_sensor_keyboards(self):
        """Find evdev devices for TemperhUM keyboard interfaces"""
        keyboards = {}
        
        try:
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            for device in devices:
                if "TEMPerHUM" in device.name:
                    # Determine which sensor this is
                    if "usb-0000:03:00.3-1" in device.phys:
                        sensor_id = "sensor1"
                    elif "usb-0000:03:00.3-2" in device.phys:
                        sensor_id = "sensor2"
                    else:
                        sensor_id = f"unknown_{device.path}"
                    
                    keyboards[sensor_id] = device
                    print(f"📱 Found {sensor_id} keyboard: {device.path} ({device.name})")
                    
        except Exception as e:
            print(f"Error finding keyboards: {e}")
        
        return keyboards
    
    def monitor_text_output(self, keyboards, duration=15):
        """Monitor keyboard devices for text output"""
        print(f"👂 Monitoring text output for {duration} seconds...")
        
        self.monitoring = True
        captured_text = {sensor_id: [] for sensor_id in keyboards.keys()}
        
        def monitor_device(sensor_id, device):
            """Monitor a single device for key events"""
            try:
                for event in device.read_loop():
                    if not self.monitoring:
                        break
                        
                    if event.type == evdev.ecodes.EV_KEY:
                        key_event = evdev.categorize(event)
                        if key_event.keystate == evdev.KeyEvent.key_down:
                            # Convert keycode to character
                            char = self.keycode_to_char(key_event.keycode)
                            if char:
                                captured_text[sensor_id].append(char)
                                self.text_queue.put((sensor_id, char, time.time()))
                                
            except Exception as e:
                print(f"Monitor error for {sensor_id}: {e}")
        
        # Start monitoring threads
        threads = []
        for sensor_id, device in keyboards.items():
            thread = threading.Thread(target=monitor_device, args=(sensor_id, device))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Collect output
        start_time = time.time()
        while time.time() - start_time < duration and self.monitoring:
            try:
                sensor_id, char, timestamp = self.text_queue.get(timeout=0.1)
                print(f"📝 {sensor_id}: '{char}'", end="", flush=True)
                
                # Check for newlines to format output
                if char == '\n':
                    print()  # New line
                    
            except queue.Empty:
                continue
        
        self.monitoring = False
        
        # Join text for each sensor
        results = {}
        for sensor_id, chars in captured_text.items():
            text = ''.join(chars)
            if text.strip():
                results[sensor_id] = text
                print(f"\n📋 {sensor_id} captured text:")
                print(f"   {repr(text)}")
        
        return results
    
    def keycode_to_char(self, keycode):
        """Convert evdev keycode to character"""
        # Basic keycode to character mapping
        keycode_map = {
            evdev.ecodes.KEY_A: 'a', evdev.ecodes.KEY_B: 'b', evdev.ecodes.KEY_C: 'c',
            evdev.ecodes.KEY_D: 'd', evdev.ecodes.KEY_E: 'e', evdev.ecodes.KEY_F: 'f',
            evdev.ecodes.KEY_G: 'g', evdev.ecodes.KEY_H: 'h', evdev.ecodes.KEY_I: 'i',
            evdev.ecodes.KEY_J: 'j', evdev.ecodes.KEY_K: 'k', evdev.ecodes.KEY_L: 'l',
            evdev.ecodes.KEY_M: 'm', evdev.ecodes.KEY_N: 'n', evdev.ecodes.KEY_O: 'o',
            evdev.ecodes.KEY_P: 'p', evdev.ecodes.KEY_Q: 'q', evdev.ecodes.KEY_R: 'r',
            evdev.ecodes.KEY_S: 's', evdev.ecodes.KEY_T: 't', evdev.ecodes.KEY_U: 'u',
            evdev.ecodes.KEY_V: 'v', evdev.ecodes.KEY_W: 'w', evdev.ecodes.KEY_X: 'x',
            evdev.ecodes.KEY_Y: 'y', evdev.ecodes.KEY_Z: 'z',
            
            evdev.ecodes.KEY_1: '1', evdev.ecodes.KEY_2: '2', evdev.ecodes.KEY_3: '3',
            evdev.ecodes.KEY_4: '4', evdev.ecodes.KEY_5: '5', evdev.ecodes.KEY_6: '6',
            evdev.ecodes.KEY_7: '7', evdev.ecodes.KEY_8: '8', evdev.ecodes.KEY_9: '9',
            evdev.ecodes.KEY_0: '0',
            
            evdev.ecodes.KEY_SPACE: ' ', evdev.ecodes.KEY_ENTER: '\n',
            evdev.ecodes.KEY_DOT: '.', evdev.ecodes.KEY_COMMA: ',',
            evdev.ecodes.KEY_SLASH: '/', evdev.ecodes.KEY_MINUS: '-',
            evdev.ecodes.KEY_LEFTBRACE: '[', evdev.ecodes.KEY_RIGHTBRACE: ']',
            evdev.ecodes.KEY_SEMICOLON: ':', evdev.ecodes.KEY_APOSTROPHE: '%',
        }
        
        return keycode_map.get(keycode, '')
    
    def test_control_with_text_monitoring(self, sensor_id, command_bytes, description):
        """Test control command while monitoring for text output"""
        print(f"\n🧪 Testing {sensor_id}: {description}")
        print(f"   Command: {[hex(b) for b in command_bytes]}")
        
        if sensor_id not in self.controller.sensors or 'control' not in self.controller.sensors[sensor_id]:
            print(f"   ❌ No control interface")
            return False
        
        # Find keyboard devices
        keyboards = self.find_sensor_keyboards()
        if sensor_id not in keyboards:
            print(f"   ❌ No keyboard interface found for {sensor_id}")
            return False
        
        print(f"   📡 Starting text monitoring...")
        
        # Start monitoring in background
        monitor_thread = threading.Thread(
            target=self.monitor_text_output, 
            args=({sensor_id: keyboards[sensor_id]}, 10)
        )
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Wait a moment for monitoring to start
        time.sleep(1)
        
        # Send control command
        control_path = self.controller.sensors[sensor_id]['control']
        success = self.controller.send_control_command(control_path, command_bytes, description)
        
        if not success:
            print(f"   ❌ Failed to send command")
            self.monitoring = False
            return False
        
        print(f"   ⏳ Waiting for text output...")
        
        # Wait for monitoring to complete
        monitor_thread.join(timeout=12)
        self.monitoring = False
        
        # Check if we got text output
        text_found = not self.text_queue.empty()
        
        if text_found:
            print(f"   🎉 TEXT OUTPUT DETECTED - COMMAND WORKED!")
            
            # Process remaining queue items
            while not self.text_queue.empty():
                try:
                    sensor_id_q, char, timestamp = self.text_queue.get_nowait()
                    print(f"📝 {sensor_id_q}: '{char}'", end="", flush=True)
                except queue.Empty:
                    break
            print()  # Final newline
            
            return True
        else:
            print(f"   ⚪ No text output detected")
            return False
    
    def run_control_discovery_with_text_monitoring(self):
        """Run control discovery using text output monitoring"""
        print("🎯 CONTROL DISCOVERY WITH TEXT OUTPUT MONITORING")
        print("=" * 50)
        
        if not self.controller.sensors:
            print("❌ No sensors found!")
            return
        
        # Test the most promising control commands
        test_commands = [
            # Toggle commands (most likely to trigger text mode)
            ([0x01, 0x81, 0x33, 0x01, 0x00, 0x00, 0x00, 0x00], "Toggle output variant 1"),
            ([0x01, 0x82, 0x33, 0x01, 0x00, 0x00, 0x00, 0x00], "Toggle output variant 2"),
            ([0x01, 0x80, 0x34, 0x01, 0x00, 0x00, 0x00, 0x00], "Modified data query"),
            ([0x01, 0x80, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00], "Toggle bit in data query"),
            
            # Caps/Num Lock simulation (based on documentation)
            ([0x01, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], "Caps Lock press"),
            ([0x01, 0x53, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], "Num Lock press"),
            ([0x01, 0x39, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00], "Double Caps Lock (++)"),
            ([0x01, 0x53, 0x53, 0x00, 0x00, 0x00, 0x00, 0x00], "Double Num Lock (--)"),
            
            # Firmware-based commands
            ([0x01, 0x86, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00], "Firmware + control 1"),
            ([0x01, 0x86, 0x02, 0x01, 0x00, 0x00, 0x00, 0x00], "Firmware + control 2"),
            
            # Interval adjustment attempts
            ([0x01, 0x80, 0x33, 0x01, 0x02, 0x00, 0x00, 0x00], "Set 2-second interval"),
            ([0x01, 0x80, 0x33, 0x01, 0x05, 0x00, 0x00, 0x00], "Set 5-second interval"),
        ]
        
        working_commands = []
        
        for sensor_id in self.controller.sensors.keys():
            print(f"\n{'='*15} TESTING {sensor_id.upper()} {'='*15}")
            
            for command, description in test_commands:
                success = self.test_control_with_text_monitoring(sensor_id, command, description)
                
                if success:
                    working_commands.append({
                        'sensor': sensor_id,
                        'command': command,
                        'description': description
                    })
                    print(f"   ✅ WORKING COMMAND FOUND!")
                    
                    # Test it again to confirm
                    print(f"   🔄 Confirming command...")
                    confirmed = self.test_control_with_text_monitoring(
                        sensor_id, command, f"CONFIRM: {description}"
                    )
                    if confirmed:
                        print(f"   ✅ CONFIRMED!")
                    else:
                        print(f"   ⚠️ Could not confirm")
                
                time.sleep(2)  # Pause between tests
        
        # Summary
        print(f"\n📋 DISCOVERY RESULTS")
        print("=" * 25)
        
        if working_commands:
            print(f"🎉 SUCCESS! Found {len(working_commands)} working commands:")
            for cmd_info in working_commands:
                print(f"  ✅ {cmd_info['sensor']}: {cmd_info['description']}")
                print(f"     Command: {[hex(b) for b in cmd_info['command']]}")
                print()
            
            print("🎯 These commands successfully triggered text output mode!")
            print("📝 Ready to integrate into temper.py!")
            
        else:
            print("❌ No working commands found")
            print("💡 Possible next steps:")
            print("   1. Try different command timing")
            print("   2. Test with different interface")
            print("   3. Check if driver is interfering")
        
        return working_commands

def main():
    if os.geteuid() != 0:
        print("❌ Need sudo for hidraw and evdev access")
        exit(1)
    
    monitor = TextOutputMonitor()
    working_commands = monitor.run_control_discovery_with_text_monitoring()
    
    # Save results for temper.py integration
    if working_commands:
        print(f"\n💾 Saving results for temper.py integration...")
        
        with open('working_control_commands.txt', 'w') as f:
            f.write("# Working TemperhUM Control Commands\n")
            f.write("# Discovered via systematic testing\n\n")
            
            for cmd in working_commands:
                f.write(f"Sensor: {cmd['sensor']}\n")
                f.write(f"Description: {cmd['description']}\n") 
                f.write(f"Command: {cmd['command']}\n")
                f.write(f"Hex: {[hex(b) for b in cmd['command']]}\n\n")
        
        print("✅ Results saved to working_control_commands.txt")

if __name__ == "__main__":
    main()