#!/usr/bin/env python3
"""
Interval Decoder - Analyze raw sensor data to find interval encoding
"""
import os
import struct
import time
import binascii
from temperhum_controller import TemperhUMController

class IntervalDecoder:
    def __init__(self):
        self.controller = TemperhUMController(verbose=True)
        
    def analyze_data_pattern(self, samples=20):
        """Collect multiple samples to analyze data pattern"""
        print("🔍 ANALYZING DATA PATTERN FOR INTERVAL ENCODING")
        print("=" * 50)
        
        samples_data = []
        
        print(f"📊 Collecting {samples} samples...")
        for i in range(samples):
            data = self.controller.read_all_sensors()
            samples_data.append(data)
            print(f"Sample {i+1:2d}: ", end="")
            
            for sensor_id, sensor_data in data.items():
                if 'raw_hex' in sensor_data:
                    raw_hex = sensor_data['raw_hex']
                    temp = sensor_data['internal_temperature_c']
                    hum = sensor_data['internal_humidity']
                    print(f"{sensor_id}={raw_hex} ({temp:.1f}°C, {hum:.1f}%) ", end="")
            print()
            time.sleep(1)
        
        # Analyze patterns
        print(f"\n🔬 PATTERN ANALYSIS:")
        print("-" * 20)
        
        for sensor_id in self.controller.sensors.keys():
            print(f"\n📡 {sensor_id.upper()} Analysis:")
            
            sensor_samples = []
            for sample in samples_data:
                if sensor_id in sample and 'raw_hex' in sample[sensor_id]:
                    sensor_samples.append(sample[sensor_id]['raw_hex'])
            
            if not sensor_samples:
                continue
                
            # Analyze each byte position
            print("   Byte Position Analysis:")
            print("   Pos:  0  1  2  3  4  5  6  7")
            print("   " + "-" * 26)
            
            for i, hex_str in enumerate(sensor_samples[:10]):  # Show first 10
                bytes_list = [hex_str[j:j+2] for j in range(0, len(hex_str), 2)]
                print(f"   {i+1:2d}: {' '.join(bytes_list)}")
            
            # Look for constant vs variable bytes
            print(f"\n   📈 Variability Analysis:")
            byte_positions = 8  # 8 bytes
            for pos in range(byte_positions):
                byte_values = set()
                for hex_str in sensor_samples:
                    if len(hex_str) >= (pos + 1) * 2:
                        byte_val = hex_str[pos*2:(pos+1)*2]
                        byte_values.add(byte_val)
                
                if len(byte_values) == 1:
                    print(f"      Byte {pos}: CONSTANT = {list(byte_values)[0]}")
                else:
                    print(f"      Byte {pos}: VARIABLE = {sorted(byte_values)} ({len(byte_values)} values)")
            
            # Decode last bytes (likely interval info)
            print(f"\n   🎯 Last 2 bytes analysis (potential interval):")
            last_bytes = []
            for hex_str in sensor_samples:
                if len(hex_str) >= 16:
                    last_2_bytes = hex_str[12:16]  # bytes 6-7
                    last_bytes.append(last_2_bytes)
            
            unique_last = set(last_bytes)
            print(f"      Last 2 bytes values: {sorted(unique_last)}")
            
            # Try to decode as interval
            for last_val in sorted(unique_last):
                try:
                    # Try as big-endian 16-bit integer
                    int_val = int(last_val, 16)
                    print(f"      {last_val} = {int_val} (decimal)")
                    
                    # Common interval interpretations
                    if int_val == 1:
                        print(f"        -> Likely 1 second interval")
                    elif int_val == 2:
                        print(f"        -> Likely 2 second interval") 
                    elif int_val == 5:
                        print(f"        -> Likely 5 second interval")
                    elif int_val == 10:
                        print(f"        -> Likely 10 second interval")
                    elif int_val in [100, 1000]:
                        print(f"        -> Likely {int_val/100:.1f} second interval (if /100)")
                    
                except:
                    pass
    
    def test_interval_control_with_monitoring(self, sensor_id, command_bytes, description):
        """Test control command while monitoring for interval changes in data"""
        print(f"\n🧪 Testing {sensor_id}: {description}")
        print(f"   Command: {[hex(b) for b in command_bytes]}")
        
        if sensor_id not in self.controller.sensors or 'control' not in self.controller.sensors[sensor_id]:
            print(f"   ❌ No control interface")
            return False
        
        # Get baseline interval encoding
        print("   📊 Getting baseline...")
        baseline_data = []
        for i in range(5):
            data = self.controller.read_all_sensors()
            if sensor_id in data and 'raw_hex' in data[sensor_id]:
                baseline_data.append(data[sensor_id]['raw_hex'])
            time.sleep(1)
        
        baseline_intervals = set()
        for hex_str in baseline_data:
            if len(hex_str) >= 16:
                interval_bytes = hex_str[12:16]  # Last 2 bytes
                baseline_intervals.add(interval_bytes)
        
        print(f"   Baseline interval encoding: {sorted(baseline_intervals)}")
        
        # Send control command
        control_path = self.controller.sensors[sensor_id]['control']
        success = self.controller.send_control_command(control_path, command_bytes, description)
        
        if not success:
            print(f"   ❌ Failed to send command")
            return False
        
        # Monitor for changes
        print("   📡 Monitoring for changes...")
        test_data = []
        for i in range(10):
            data = self.controller.read_all_sensors()
            if sensor_id in data and 'raw_hex' in data[sensor_id]:
                test_data.append(data[sensor_id]['raw_hex'])
                
                # Show real-time interval decoding
                hex_str = data[sensor_id]['raw_hex']
                if len(hex_str) >= 16:
                    interval_bytes = hex_str[12:16]
                    int_val = int(interval_bytes, 16) if interval_bytes != '0000' else 0
                    print(f"      Sample {i+1}: {hex_str} -> interval: {interval_bytes} ({int_val})")
            
            time.sleep(1)
        
        # Analyze results
        test_intervals = set()
        for hex_str in test_data:
            if len(hex_str) >= 16:
                interval_bytes = hex_str[12:16]
                test_intervals.add(interval_bytes)
        
        print(f"   Test interval encoding: {sorted(test_intervals)}")
        
        # Check for changes
        if test_intervals != baseline_intervals:
            print(f"   🎉 INTERVAL CHANGE DETECTED!")
            print(f"      Before: {sorted(baseline_intervals)}")
            print(f"      After:  {sorted(test_intervals)}")
            return True
        else:
            print(f"   ⚪ No interval change detected")
            return False
    
    def run_focused_control_test(self):
        """Run focused control test using interval monitoring"""
        print("🎯 FOCUSED CONTROL TEST WITH INTERVAL MONITORING")
        print("=" * 50)
        
        # First, analyze the data pattern
        self.analyze_data_pattern(samples=10)
        
        # Test promising control commands
        test_commands = [
            # Interval adjustment commands (most likely to show changes)
            ([0x01, 0x80, 0x33, 0x01, 0x02, 0x00, 0x00, 0x00], "Set 2-second interval"),
            ([0x01, 0x80, 0x33, 0x01, 0x05, 0x00, 0x00, 0x00], "Set 5-second interval"),
            ([0x01, 0x80, 0x33, 0x01, 0x01, 0x00, 0x00, 0x00], "Set 1-second interval"),
            
            # Toggle commands
            ([0x01, 0x81, 0x33, 0x01, 0x00, 0x00, 0x00, 0x00], "Toggle output"),
            ([0x01, 0x82, 0x33, 0x01, 0x00, 0x00, 0x00, 0x00], "Toggle variant"),
            
            # Caps/Num Lock simulation
            ([0x01, 0x39, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00], "Double Caps Lock (increase)"),
            ([0x01, 0x53, 0x53, 0x00, 0x00, 0x00, 0x00, 0x00], "Double Num Lock (decrease)"),
        ]
        
        working_commands = []
        
        for sensor_id in self.controller.sensors.keys():
            print(f"\n{'='*15} TESTING {sensor_id.upper()} {'='*15}")
            
            for command, description in test_commands:
                success = self.test_interval_control_with_monitoring(sensor_id, command, description)
                
                if success:
                    working_commands.append({
                        'sensor': sensor_id,
                        'command': command,
                        'description': description
                    })
                    print(f"   ✅ WORKING COMMAND FOUND!")
                
                time.sleep(3)  # Pause between tests
        
        # Summary
        print(f"\n📋 RESULTS SUMMARY")
        print("=" * 20)
        
        if working_commands:
            print(f"✅ Found {len(working_commands)} working commands:")
            for cmd_info in working_commands:
                print(f"  • {cmd_info['sensor']}: {cmd_info['description']}")
                print(f"    Command: {[hex(b) for b in cmd_info['command']]}")
        else:
            print("❌ No working commands found")
        
        return working_commands

def main():
    if os.geteuid() != 0:
        print("❌ Need sudo for hidraw access")
        exit(1)
    
    decoder = IntervalDecoder()
    decoder.run_focused_control_test()

if __name__ == "__main__":
    main()