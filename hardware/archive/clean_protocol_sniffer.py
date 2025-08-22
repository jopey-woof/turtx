#!/usr/bin/env python3
"""
Clean Protocol Sniffer - Focus on non-zero HID commands to reverse engineer protocol
"""
import os
import time
import threading
import select
from queue import Queue, Empty

class CleanProtocolSniffer:
    def __init__(self):
        self.data_queue = Queue()
        self.running = True
        self.command_log = []
        
    def find_temperhum_hidraw_devices(self):
        """Find TemperhUM hidraw devices"""
        devices = []
        for i in range(20):
            hidraw_path = f'/dev/hidraw{i}'
            if os.path.exists(hidraw_path):
                try:
                    link = os.readlink(f'/sys/class/hidraw/hidraw{i}')
                    if '3553' in link:
                        # Determine which USB device and interface
                        if '1-1:1.0' in link:
                            device_info = {'path': hidraw_path, 'usb': '1-1', 'interface': 0, 'desc': 'Sensor1-Interface0'}
                        elif '1-1:1.1' in link:
                            device_info = {'path': hidraw_path, 'usb': '1-1', 'interface': 1, 'desc': 'Sensor1-Interface1'}
                        elif '1-2:1.0' in link:
                            device_info = {'path': hidraw_path, 'usb': '1-2', 'interface': 0, 'desc': 'Sensor2-Interface0'}
                        elif '1-2:1.1' in link:
                            device_info = {'path': hidraw_path, 'usb': '1-2', 'interface': 1, 'desc': 'Sensor2-Interface1'}
                        else:
                            device_info = {'path': hidraw_path, 'usb': 'unknown', 'interface': -1, 'desc': f'Unknown-{hidraw_path}'}
                        
                        devices.append(device_info)
                except:
                    pass
        
        return devices
    
    def is_significant_command(self, data_bytes):
        """Check if this is a significant (non-zero, non-repetitive) command"""
        # All zeros = key release, ignore
        if all(b == 0 for b in data_bytes):
            return False
        
        # Single character typing (third byte is keycode, others mostly zero)
        # This is normal sensor data output, not control commands
        if data_bytes[0] == 0 and data_bytes[1] == 0 and data_bytes[2] != 0 and all(b == 0 for b in data_bytes[3:]):
            return False
        
        # Shift + character (first byte = 0x2, third byte = keycode)
        # Also normal sensor data output  
        if data_bytes[0] == 2 and data_bytes[1] == 0 and data_bytes[2] != 0 and all(b == 0 for b in data_bytes[3:]):
            return False
        
        # If we get here, it might be a control command
        return True
    
    def analyze_command(self, data_bytes):
        """Analyze a command to understand its purpose"""
        if data_bytes[0] != 0:
            return f"Modifier: 0x{data_bytes[0]:02x}"
        elif data_bytes[2] == 0x39:
            return "Caps Lock"
        elif data_bytes[2] == 0x53:
            return "Num Lock"
        else:
            return f"Key: 0x{data_bytes[2]:02x}"
    
    def sniff_hidraw_device(self, device_info):
        """Sniff HID data from a single device, focusing on significant commands"""
        device_path = device_info['path']
        desc = device_info['desc']
        
        try:
            with open(device_path, 'rb') as f:
                last_command = None
                repeat_count = 0
                
                while self.running:
                    ready, _, _ = select.select([f], [], [], 0.1)
                    
                    if ready:
                        try:
                            data = f.read(8)
                            if data:
                                data_bytes = list(data)
                                
                                # Only process significant commands
                                if self.is_significant_command(data_bytes):
                                    # Avoid spam from repeated commands
                                    if data_bytes == last_command:
                                        repeat_count += 1
                                        if repeat_count > 3:  # Only show first few repeats
                                            continue
                                    else:
                                        repeat_count = 0
                                        last_command = data_bytes.copy()
                                    
                                    timestamp = time.time()
                                    self.data_queue.put({
                                        'timestamp': timestamp,
                                        'device': desc,
                                        'data': data_bytes,
                                        'hex': [f'0x{b:02x}' for b in data_bytes],
                                        'analysis': self.analyze_command(data_bytes)
                                    })
                        except Exception as e:
                            if self.running:
                                print(f"Error reading from {desc}: {e}")
                            break
                    
        except PermissionError:
            print(f"❌ Permission denied for {desc} - need sudo")
        except Exception as e:
            print(f"❌ Error with {desc}: {e}")
    
    def display_clean_commands(self):
        """Display only significant HID commands"""
        print(f"\n🎯 CLEAN PROTOCOL CAPTURE")
        print("=" * 50)
        print("Showing only significant commands (filtering out normal typing)")
        print("Press the physical button on sensors now...")
        print("Press Ctrl+C to stop")
        print()
        
        command_count = 0
        
        try:
            while self.running:
                try:
                    capture = self.data_queue.get(timeout=1.0)
                    
                    timestamp = time.strftime("%H:%M:%S.%f", time.localtime(capture['timestamp']))[:-3]
                    device = capture['device']
                    data_bytes = capture['data']
                    hex_data = capture['hex']
                    analysis = capture['analysis']
                    
                    command_count += 1
                    
                    print(f"[{timestamp}] {device}:")
                    print(f"  Command #{command_count}")
                    print(f"  Raw: {data_bytes}")
                    print(f"  Hex: {hex_data}")
                    print(f"  Analysis: {analysis}")
                    
                    # Store for later analysis
                    self.command_log.append({
                        'timestamp': capture['timestamp'],
                        'device': device,
                        'command': data_bytes,
                        'analysis': analysis
                    })
                    
                    print()
                    
                except Empty:
                    if command_count == 0:
                        print(".", end="", flush=True)
                    continue
                except KeyboardInterrupt:
                    break
                    
        except KeyboardInterrupt:
            pass
        
        print(f"\n🛑 Capture stopped - {command_count} significant commands captured")
    
    def summarize_findings(self):
        """Summarize the captured commands"""
        if not self.command_log:
            print("No significant commands captured")
            return
        
        print(f"\n📋 PROTOCOL ANALYSIS SUMMARY")
        print("=" * 40)
        print(f"Total significant commands: {len(self.command_log)}")
        
        # Group by device
        by_device = {}
        for cmd in self.command_log:
            device = cmd['device']
            if device not in by_device:
                by_device[device] = []
            by_device[device].append(cmd)
        
        for device, commands in by_device.items():
            print(f"\n{device}: {len(commands)} commands")
            
            # Show unique command patterns
            unique_commands = {}
            for cmd in commands:
                cmd_key = tuple(cmd['command'])
                if cmd_key not in unique_commands:
                    unique_commands[cmd_key] = {'count': 0, 'analysis': cmd['analysis']}
                unique_commands[cmd_key]['count'] += 1
            
            for cmd_bytes, info in unique_commands.items():
                hex_str = ' '.join([f'0x{b:02x}' for b in cmd_bytes])
                print(f"  {hex_str} - {info['analysis']} ({info['count']}x)")
        
        print(f"\n🔧 NEXT STEPS:")
        print("1. Try sending these exact command sequences programmatically")
        print("2. Test different timing between press/release")
        print("3. Try sending to different interfaces")
    
    def run_clean_sniffer(self):
        """Run the clean protocol sniffer"""
        print("🕵️  CLEAN PROTOCOL SNIFFER")
        print("=" * 35)
        print("Filtering out normal typing, focusing on control commands")
        print()
        
        # Find devices
        devices = self.find_temperhum_hidraw_devices()
        
        if not devices:
            print("❌ No TemperhUM hidraw devices found!")
            return False
        
        print(f"📡 Found {len(devices)} TemperhUM hidraw devices:")
        for device in devices:
            print(f"  {device['desc']}: {device['path']}")
        
        if os.geteuid() != 0:
            print(f"❌ Not running as root. Please run with:")
            print(f"sudo python3 clean_protocol_sniffer.py")
            return False
        
        # Start sniffers
        threads = []
        for device in devices:
            thread = threading.Thread(target=self.sniff_hidraw_device, args=(device,), daemon=True)
            thread.start()
            threads.append(thread)
        
        # Display commands
        self.display_clean_commands()
        
        # Stop and summarize
        self.running = False
        self.summarize_findings()
        
        return True

def main():
    sniffer = CleanProtocolSniffer()
    sniffer.run_clean_sniffer()

if __name__ == "__main__":
    main()