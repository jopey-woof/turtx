#!/usr/bin/env python3
"""
HID Protocol Sniffer - Capture raw HID data from button presses to reverse engineer the protocol
"""
import os
import time
import threading
import select
from queue import Queue, Empty

class HIDProtocolSniffer:
    def __init__(self):
        self.temperhum_hidraw_devices = []
        self.data_queue = Queue()
        self.running = True
        
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
    
    def sniff_hidraw_device(self, device_info):
        """Sniff HID data from a single device"""
        device_path = device_info['path']
        desc = device_info['desc']
        
        try:
            print(f"📡 Starting sniffer for {desc} ({device_path})")
            
            with open(device_path, 'rb') as f:
                while self.running:
                    # Use select to check if data is available (non-blocking)
                    ready, _, _ = select.select([f], [], [], 0.1)
                    
                    if ready:
                        try:
                            # Read raw HID report
                            data = f.read(8)  # HID reports are typically 8 bytes
                            if data:
                                timestamp = time.time()
                                self.data_queue.put({
                                    'timestamp': timestamp,
                                    'device': desc,
                                    'data': list(data),
                                    'hex': [hex(b) for b in data]
                                })
                        except Exception as e:
                            if self.running:
                                print(f"Error reading from {desc}: {e}")
                            break
                    
        except PermissionError:
            print(f"❌ Permission denied for {desc} - need sudo")
        except Exception as e:
            print(f"❌ Error with {desc}: {e}")
    
    def display_captured_data(self):
        """Display captured HID data in real-time"""
        print(f"\n🎯 LIVE HID DATA CAPTURE")
        print("=" * 60)
        print("Press buttons on sensors now...")
        print("Press Ctrl+C to stop")
        print()
        
        last_data = {}
        
        try:
            while self.running:
                try:
                    # Get data with timeout
                    capture = self.data_queue.get(timeout=0.5)
                    
                    timestamp = time.strftime("%H:%M:%S", time.localtime(capture['timestamp']))
                    device = capture['device']
                    data_bytes = capture['data']
                    hex_data = capture['hex']
                    
                    # Check if this is different from the last data for this device
                    if device not in last_data or last_data[device] != data_bytes:
                        print(f"[{timestamp}] {device}:")
                        print(f"  Raw bytes: {data_bytes}")
                        print(f"  Hex:       {hex_data}")
                        
                        # Analyze the data
                        if all(b == 0 for b in data_bytes):
                            print(f"  Analysis:  🔄 All zeros (key release)")
                        elif data_bytes[2] == 0x39:  # Caps Lock
                            print(f"  Analysis:  🔒 Caps Lock detected")
                        elif data_bytes[2] == 0x53:  # Num Lock
                            print(f"  Analysis:  🔢 Num Lock detected")
                        else:
                            print(f"  Analysis:  ❓ Unknown command")
                        
                        print()
                        last_data[device] = data_bytes.copy()
                    
                except Empty:
                    continue
                except KeyboardInterrupt:
                    break
                    
        except KeyboardInterrupt:
            pass
        
        print(f"\n🛑 Capture stopped")
    
    def run_protocol_sniffer(self):
        """Run the HID protocol sniffer"""
        print("🕵️  HID PROTOCOL SNIFFER")
        print("=" * 35)
        print("Reverse engineering TemperhUM protocol by observing button presses")
        print()
        
        # Find devices
        devices = self.find_temperhum_hidraw_devices()
        
        if not devices:
            print("❌ No TemperhUM hidraw devices found!")
            return False
        
        print(f"📡 Found {len(devices)} TemperhUM hidraw devices:")
        for device in devices:
            print(f"  {device['desc']}: {device['path']}")
        
        print(f"\n⚠️  This tool requires sudo to read hidraw devices")
        
        # Check if running as root
        if os.geteuid() != 0:
            print(f"❌ Not running as root. Please run with:")
            print(f"sudo python3 hid_protocol_sniffer.py")
            return False
        
        # Start sniffers for all devices
        threads = []
        for device in devices:
            thread = threading.Thread(target=self.sniff_hidraw_device, args=(device,), daemon=True)
            thread.start()
            threads.append(thread)
        
        # Display captured data
        self.display_captured_data()
        
        # Stop all threads
        self.running = False
        
        print(f"\n📋 INSTRUCTIONS FOR NEXT STEP:")
        print("1. Review the captured HID data above")
        print("2. Note the exact byte sequences for each button action")
        print("3. Use those exact sequences in a new control script")
        print("4. Test programmatic control with the observed protocol")
        
        return True

def main():
    sniffer = HIDProtocolSniffer()
    sniffer.run_protocol_sniffer()

if __name__ == "__main__":
    main()