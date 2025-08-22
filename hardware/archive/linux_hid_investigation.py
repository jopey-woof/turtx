#!/usr/bin/env python3
"""
Linux HID Investigation - Investigate Linux-specific HID handling differences
"""
import os
import subprocess
import time

class LinuxHIDInvestigation:
    def __init__(self):
        self.findings = []
        
    def get_hid_report_descriptor(self, hidraw_path):
        """Get HID report descriptor for a device"""
        try:
            # Use hidrd-convert to get report descriptor if available
            result = subprocess.run(['hexdump', '-C', f'/sys/class/hidraw/{os.path.basename(hidraw_path)}/device/report_descriptor'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    def check_hid_drivers(self):
        """Check which HID drivers are loaded and their quirks"""
        print("🔍 LINUX HID DRIVER INVESTIGATION")
        print("=" * 45)
        
        # Check loaded HID modules
        try:
            result = subprocess.run(['lsmod'], capture_output=True, text=True)
            hid_modules = [line for line in result.stdout.split('\n') if 'hid' in line.lower()]
            
            print("📋 Loaded HID modules:")
            for module in hid_modules:
                print(f"  {module}")
        except:
            print("❌ Could not check loaded modules")
        
        print()
        
        # Check for HID quirks
        quirks_files = [
            '/sys/module/usbhid/parameters/quirks',
            '/proc/bus/input/devices'
        ]
        
        for quirks_file in quirks_files:
            if os.path.exists(quirks_file):
                print(f"📄 {quirks_file}:")
                try:
                    with open(quirks_file, 'r') as f:
                        content = f.read().strip()
                        if '3553' in content or 'TEMPerHUM' in content:
                            print(f"  🎯 TemperhUM found: {content}")
                        else:
                            print(f"  ℹ️ No TemperhUM entries")
                except:
                    print(f"  ❌ Could not read file")
                print()
    
    def check_device_capabilities(self):
        """Check device capabilities and report descriptors"""
        print("🔧 DEVICE CAPABILITIES ANALYSIS")
        print("=" * 35)
        
        # Find TemperhUM devices
        for i in range(10):
            hidraw_path = f'/dev/hidraw{i}'
            if os.path.exists(hidraw_path):
                try:
                    link = os.readlink(f'/sys/class/hidraw/hidraw{i}')
                    if '3553' in link:
                        print(f"\n📱 {hidraw_path} ({link}):")
                        
                        # Check device info
                        device_dir = f'/sys/class/hidraw/hidraw{i}/device'
                        
                        info_files = ['modalias', 'bInterfaceNumber', 'bInterfaceClass', 'bInterfaceProtocol']
                        for info_file in info_files:
                            info_path = os.path.join(device_dir, info_file)
                            if os.path.exists(info_path):
                                try:
                                    with open(info_path, 'r') as f:
                                        value = f.read().strip()
                                        print(f"  {info_file}: {value}")
                                except:
                                    pass
                        
                        # Try to get report descriptor
                        report_desc = self.get_hid_report_descriptor(hidraw_path)
                        if report_desc:
                            print(f"  Report descriptor: {report_desc[:100]}...")
                        
                except Exception as e:
                    pass
    
    def test_linux_specific_methods(self):
        """Test Linux-specific HID interaction methods"""
        print("\n🐧 LINUX-SPECIFIC METHODS TEST")
        print("=" * 35)
        
        # Find TemperhUM control interfaces
        control_devices = []
        for i in range(10):
            hidraw_path = f'/dev/hidraw{i}'
            if os.path.exists(hidraw_path):
                try:
                    link = os.readlink(f'/sys/class/hidraw/hidraw{i}')
                    if '3553' in link and '1.1' in link:  # Interface 1 = control
                        control_devices.append(hidraw_path)
                except:
                    pass
        
        if not control_devices:
            print("❌ No control interfaces found")
            return
        
        print(f"📡 Found {len(control_devices)} control interfaces:")
        for device in control_devices:
            print(f"  {device}")
        
        # Test Linux-specific approaches
        for device_path in control_devices:
            print(f"\n🎯 Testing {device_path}:")
            
            # Method 1: ioctl-based HID commands
            print("  Method 1: Direct ioctl...")
            try:
                import fcntl
                import struct
                
                with open(device_path, 'r+b') as f:
                    # Try HID feature report
                    feature_data = bytearray([0x01, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                    # HIDIOCSFEATURE ioctl
                    fcntl.ioctl(f.fileno(), 0xC0084806, feature_data)
                    print("    ✅ ioctl command sent")
                    time.sleep(1)
            except Exception as e:
                print(f"    ❌ ioctl failed: {e}")
            
            # Method 2: Raw write with different formats
            print("  Method 2: Raw writes with Linux timing...")
            try:
                with open(device_path, 'wb') as f:
                    # Try Windows-style timing
                    commands = [
                        ([0x00, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00], 0.1),  # Press
                        ([0x00, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00], 1.0),  # Hold
                        ([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0.1),  # Release
                    ]
                    
                    for cmd, delay in commands:
                        f.write(bytes(cmd))
                        f.flush()
                        time.sleep(delay)
                    
                    print("    ✅ Raw write sequence completed")
            except Exception as e:
                print(f"    ❌ Raw write failed: {e}")
            
            # Method 3: Try unbinding and rebinding driver
            print("  Method 3: Driver rebind test...")
            try:
                # Get the HID device path
                link = os.readlink(f'/sys/class/hidraw/{os.path.basename(device_path)}')
                hid_device = os.path.basename(link.split('/')[-2])
                
                print(f"    HID device: {hid_device}")
                
                # Try to unbind and rebind (requires root)
                unbind_path = f'/sys/bus/hid/drivers/hid-generic/unbind'
                bind_path = f'/sys/bus/hid/drivers/hid-generic/bind'
                
                if os.path.exists(unbind_path):
                    with open(unbind_path, 'w') as f:
                        f.write(hid_device)
                    print("    ✅ Unbound HID device")
                    
                    time.sleep(0.5)
                    
                    with open(bind_path, 'w') as f:
                        f.write(hid_device)
                    print("    ✅ Rebound HID device")
                else:
                    print("    ⚠️ No unbind path found")
                    
            except Exception as e:
                print(f"    ❌ Driver rebind failed: {e}")
    
    def suggest_solutions(self):
        """Suggest potential solutions based on findings"""
        print("\n💡 POTENTIAL SOLUTIONS")
        print("=" * 25)
        
        solutions = [
            "1. Kernel Module Parameter: Try adding usbhid quirks for TemperhUM",
            "2. Driver Replacement: Use libusb to bypass kernel HID driver",
            "3. Windows Compatibility: Use Wine/Windows VM for sensor control",
            "4. Firmware Investigation: Check if sensors have Linux-specific firmware mode",
            "5. HID Report Format: Try different HID report structures",
            "6. Timing Differences: Adjust command timing for Linux HID stack",
            "7. Permission Issues: Ensure proper udev rules for device access"
        ]
        
        for solution in solutions:
            print(f"  {solution}")
        
        print(f"\n🔧 IMMEDIATE TESTS TO TRY:")
        print("1. Test on a Windows machine/VM to confirm working protocol")
        print("2. Try different USB ports or USB hubs")
        print("3. Check dmesg for HID-related errors during command attempts")
        print("4. Try with different kernel versions or HID drivers")
    
    def run_investigation(self):
        """Run complete Linux HID investigation"""
        if os.geteuid() != 0:
            print("⚠️ Running without root - some tests may be limited")
            print("For full investigation, run with: sudo python3 linux_hid_investigation.py")
            print()
        
        self.check_hid_drivers()
        self.check_device_capabilities()
        
        if os.geteuid() == 0:
            self.test_linux_specific_methods()
        
        self.suggest_solutions()

def main():
    investigation = LinuxHIDInvestigation()
    investigation.run_investigation()

if __name__ == "__main__":
    main()