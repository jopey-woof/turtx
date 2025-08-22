#!/usr/bin/env python3
"""
Advanced HID Sniffer - Reverse engineer button press with HID descriptor knowledge
"""
import os
import time
import threading
import struct
import select

class AdvancedHIDSniffer:
    def __init__(self):
        self.running = False
        self.interfaces = {}
        self.capture_data = []
        
    def analyze_hid_descriptors(self):
        """Analyze the HID descriptors we discovered"""
        print("🔍 HID DESCRIPTOR ANALYSIS")
        print("=" * 30)
        
        descriptors = {
            "Interface 0 (Keyboard/Output)": {
                "raw": "05 01 09 06 a1 01 05 07 19 e0 29 e7 15 00 25 01 75 01 95 08",
                "meaning": [
                    "05 01    - Usage Page (Generic Desktop)",
                    "09 06    - Usage (Keyboard)", 
                    "a1 01    - Collection (Application)",
                    "05 07    - Usage Page (Keyboard/Keypad)",
                    "19 e0    - Usage Minimum (Left Control)",
                    "29 e7    - Usage Maximum (Right GUI)",
                    "15 00    - Logical Minimum (0)",
                    "25 01    - Logical Maximum (1)",
                    "75 01    - Report Size (1 bit)",
                    "95 08    - Report Count (8)"
                ],
                "format": "Standard 8-byte keyboard HID report"
            },
            "Interface 1 (Generic/Control)": {
                "raw": "05 01 09 00 a1 01 09 01 15 00 25 ff 95 08 75 08 81 02",
                "meaning": [
                    "05 01    - Usage Page (Generic Desktop)",
                    "09 00    - Usage (Undefined/Generic)",
                    "a1 01    - Collection (Application)",
                    "09 01    - Usage (Pointer)",
                    "15 00    - Logical Minimum (0)",
                    "25 ff    - Logical Maximum (255)",
                    "95 08    - Report Count (8)",
                    "75 08    - Report Size (8 bits)",
                    "81 02    - Input (Data, Variable, Absolute)"
                ],
                "format": "Generic 8-byte data report (0-255 per byte)"
            }
        }
        
        for interface, info in descriptors.items():
            print(f"\n📱 {interface}:")
            print(f"   Format: {info['format']}")
            print("   Descriptor breakdown:")
            for line in info['meaning']:
                print(f"     {line}")
        
        print(f"\n🎯 KEY INSIGHTS:")
        print("• Interface 0: Standard keyboard - expects modifier+keycode format")
        print("• Interface 1: Generic HID - expects 8 bytes of 0-255 values")
        print("• Button press should generate reports on Interface 1 (control)")
        print("• We need to capture Interface 1 traffic during button press")
    
    def setup_interfaces(self):
        """Setup interface monitoring"""
        print(f"\n🔧 SETTING UP INTERFACE MONITORING")
        print("-" * 35)
        
        # Find all TemperhUM interfaces
        for i in range(20):
            hidraw_path = f'/dev/hidraw{i}'
            if os.path.exists(hidraw_path):
                try:
                    link = os.readlink(f'/sys/class/hidraw/hidraw{i}')
                    if '3553' in link:
                        if '1.0' in link:
                            interface_type = "Keyboard/Output"
                            sensor_num = "1" if "1-1:" in link else "2"
                        elif '1.1' in link:
                            interface_type = "Generic/Control" 
                            sensor_num = "1" if "1-1:" in link else "2"
                        else:
                            continue
                        
                        self.interfaces[hidraw_path] = {
                            'type': interface_type,
                            'sensor': sensor_num,
                            'path': hidraw_path,
                            'fd': None
                        }
                        
                        print(f"📡 {hidraw_path}: Sensor {sensor_num} {interface_type}")
                        
                except Exception as e:
                    pass
        
        if not self.interfaces:
            print("❌ No TemperhUM interfaces found!")
            return False
        
        # Open file descriptors for reading
        opened_count = 0
        for path, info in self.interfaces.items():
            try:
                info['fd'] = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
                opened_count += 1
                print(f"✅ Opened {path} for monitoring")
            except Exception as e:
                print(f"❌ Failed to open {path}: {e}")
        
        print(f"\n📊 Successfully opened {opened_count}/{len(self.interfaces)} interfaces")
        return opened_count > 0
    
    def decode_hid_report(self, interface_info, data):
        """Decode HID report based on interface type"""
        if not data:
            return None
        
        decoded = {
            'timestamp': time.time(),
            'interface': interface_info['path'],
            'sensor': interface_info['sensor'],
            'type': interface_info['type'],
            'raw_bytes': [f"{b:02x}" for b in data],
            'length': len(data)
        }
        
        if interface_info['type'] == "Keyboard/Output":
            # Standard keyboard HID report format
            if len(data) >= 8:
                decoded.update({
                    'modifiers': f"{data[0]:08b}",
                    'reserved': f"{data[1]:02x}",
                    'keycodes': [f"{data[i]:02x}" for i in range(2, 8)],
                    'interpretation': self.interpret_keyboard_report(data)
                })
        
        elif interface_info['type'] == "Generic/Control":
            # Generic HID report - 8 bytes of data
            decoded.update({
                'data_bytes': [f"{b:02x}" for b in data[:8]],
                'interpretation': self.interpret_generic_report(data)
            })
        
        return decoded
    
    def interpret_keyboard_report(self, data):
        """Interpret keyboard HID report"""
        if len(data) < 8:
            return "Invalid keyboard report"
        
        modifiers = data[0]
        keycodes = [data[i] for i in range(2, 8) if data[i] != 0]
        
        modifier_names = []
        if modifiers & 0x01: modifier_names.append("LCtrl")
        if modifiers & 0x02: modifier_names.append("LShift") 
        if modifiers & 0x04: modifier_names.append("LAlt")
        if modifiers & 0x08: modifier_names.append("LGui")
        if modifiers & 0x10: modifier_names.append("RCtrl")
        if modifiers & 0x20: modifier_names.append("RShift")
        if modifiers & 0x40: modifier_names.append("RAlt")
        if modifiers & 0x80: modifier_names.append("RGui")
        
        # Key code mappings (partial)
        key_map = {
            0x39: "CapsLock", 0x53: "NumLock", 0x47: "ScrollLock",
            0x04: "A", 0x05: "B", 0x06: "C", 0x07: "D"
        }
        
        key_names = [key_map.get(k, f"Key_{k:02x}") for k in keycodes]
        
        parts = []
        if modifier_names:
            parts.append(f"Modifiers: {'+'.join(modifier_names)}")
        if key_names:
            parts.append(f"Keys: {'+'.join(key_names)}")
        
        return " | ".join(parts) if parts else "No keys pressed"
    
    def interpret_generic_report(self, data):
        """Interpret generic HID report"""
        if not data:
            return "Empty report"
        
        # Look for patterns that might indicate commands
        if all(b == 0 for b in data):
            return "All zeros (idle/release)"
        
        non_zero = [(i, b) for i, b in enumerate(data) if b != 0]
        if non_zero:
            positions = [f"Byte{i}={b:02x}" for i, b in non_zero]
            return f"Data: {', '.join(positions)}"
        
        return "Unknown pattern"
    
    def monitor_interfaces(self):
        """Monitor all interfaces for HID reports"""
        print(f"\n🎧 MONITORING HID INTERFACES")
        print("-" * 30)
        print("Press the button on any sensor now...")
        print("Press Ctrl+C to stop monitoring")
        print()
        
        self.running = True
        self.capture_data = []
        
        try:
            while self.running:
                # Use select to wait for data on any interface
                fds = [info['fd'] for info in self.interfaces.values() if info['fd']]
                
                if not fds:
                    break
                
                ready_fds, _, _ = select.select(fds, [], [], 0.1)
                
                for fd in ready_fds:
                    # Find which interface this fd belongs to
                    interface_info = None
                    for info in self.interfaces.values():
                        if info['fd'] == fd:
                            interface_info = info
                            break
                    
                    if interface_info:
                        try:
                            data = os.read(fd, 64)  # Read up to 64 bytes
                            if data:
                                decoded = self.decode_hid_report(interface_info, data)
                                if decoded:
                                    self.capture_data.append(decoded)
                                    self.print_hid_report(decoded)
                        except OSError:
                            pass  # No data available
                
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            print(f"\n🛑 Monitoring stopped by user")
        
        self.running = False
    
    def print_hid_report(self, decoded):
        """Print decoded HID report"""
        timestamp = time.strftime("%H:%M:%S.%f", time.localtime(decoded['timestamp']))[:12]
        
        print(f"⚡ {timestamp} | Sensor {decoded['sensor']} | {decoded['type']}")
        print(f"   Raw: [{' '.join(decoded['raw_bytes'])}]")
        print(f"   {decoded['interpretation']}")
        
        # Special handling for non-zero generic reports
        if decoded['type'] == "Generic/Control" and not all(b == '00' for b in decoded['raw_bytes']):
            print(f"   🎯 POTENTIAL CONTROL COMMAND DETECTED!")
        
        print()
    
    def cleanup(self):
        """Clean up file descriptors"""
        for info in self.interfaces.values():
            if info['fd']:
                try:
                    os.close(info['fd'])
                except:
                    pass
    
    def analyze_capture_results(self):
        """Analyze captured data for patterns"""
        if not self.capture_data:
            print("❌ No HID reports captured")
            return
        
        print(f"\n📊 CAPTURE ANALYSIS")
        print("=" * 20)
        print(f"Total reports captured: {len(self.capture_data)}")
        
        # Group by interface type
        keyboard_reports = [r for r in self.capture_data if r['type'] == "Keyboard/Output"]
        generic_reports = [r for r in self.capture_data if r['type'] == "Generic/Control"]
        
        print(f"Keyboard reports: {len(keyboard_reports)}")
        print(f"Generic reports: {len(generic_reports)}")
        
        # Look for interesting generic reports (non-zero)
        interesting_generic = [r for r in generic_reports if not all(b == '00' for b in r['raw_bytes'])]
        
        print(f"\n🎯 INTERESTING GENERIC REPORTS: {len(interesting_generic)}")
        if interesting_generic:
            print("These are likely the control commands!")
            for i, report in enumerate(interesting_generic):
                print(f"  {i+1}. [{' '.join(report['raw_bytes'])}] - {report['interpretation']}")
        else:
            print("No non-zero generic reports found - button may be internal only")
    
    def run_advanced_sniffing(self):
        """Run the complete advanced HID sniffing process"""
        if os.geteuid() != 0:
            print("❌ Need sudo for hidraw access")
            print("Run: sudo python3 advanced_hid_sniffer.py")
            return False
        
        print("🕵️ ADVANCED HID REVERSE ENGINEERING")
        print("=" * 40)
        
        # Step 1: Analyze descriptors
        self.analyze_hid_descriptors()
        
        # Step 2: Setup monitoring
        if not self.setup_interfaces():
            return False
        
        # Step 3: Monitor for button presses
        try:
            self.monitor_interfaces()
        finally:
            self.cleanup()
        
        # Step 4: Analyze results
        self.analyze_capture_results()
        
        return True

def main():
    sniffer = AdvancedHIDSniffer()
    sniffer.run_advanced_sniffing()

if __name__ == "__main__":
    main()