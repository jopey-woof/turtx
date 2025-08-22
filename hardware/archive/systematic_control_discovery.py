#!/usr/bin/env python3
"""
Systematic Control Discovery - Exhaustively test control command formats
"""
import os
import struct
import time
import threading
from temperhum_controller import TemperhUMController

class ControlDiscovery:
    def __init__(self, verbose=True):
        self.controller = TemperhUMController(verbose=verbose)
        self.baseline_readings = {}
        self.test_results = []
        
    def get_baseline(self, duration=10):
        """Establish baseline sensor behavior"""
        print(f"📊 Establishing baseline for {duration} seconds...")
        
        readings = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            data = self.controller.read_all_sensors()
            readings.append({
                'timestamp': time.time(),
                'data': data
            })
            time.sleep(0.5)
        
        # Calculate intervals
        for sensor_id in self.controller.sensors.keys():
            sensor_readings = [r for r in readings if sensor_id in r['data']]
            if len(sensor_readings) > 1:
                intervals = []
                for i in range(1, len(sensor_readings)):
                    interval = sensor_readings[i]['timestamp'] - sensor_readings[i-1]['timestamp']
                    intervals.append(interval)
                
                avg_interval = sum(intervals) / len(intervals)
                self.baseline_readings[sensor_id] = {
                    'avg_interval': avg_interval,
                    'readings_count': len(sensor_readings),
                    'total_time': duration
                }
                
                print(f"  {sensor_id}: {avg_interval:.2f}s average interval ({len(sensor_readings)} readings)")
    
    def test_control_command(self, sensor_id, command_bytes, description, monitor_time=10):
        """Test a control command and monitor for changes"""
        print(f"\n🧪 Testing {sensor_id}: {description}")
        print(f"   Command: {[hex(b) for b in command_bytes]}")
        
        if sensor_id not in self.controller.sensors or 'control' not in self.controller.sensors[sensor_id]:
            print(f"   ❌ No control interface")
            return False
        
        # Send command
        control_path = self.controller.sensors[sensor_id]['control']
        success = self.controller.send_control_command(control_path, command_bytes, description)
        
        if not success:
            print(f"   ❌ Failed to send command")
            return False
        
        # Monitor for changes
        print(f"   📡 Monitoring for {monitor_time}s...")
        readings = []
        start_time = time.time()
        
        while time.time() - start_time < monitor_time:
            data = self.controller.read_all_sensors()
            if sensor_id in data:
                readings.append({
                    'timestamp': time.time(),
                    'temp': data[sensor_id].get('internal_temperature_c'),
                    'humidity': data[sensor_id].get('internal_humidity')
                })
            time.sleep(0.5)
        
        # Analyze results
        if len(readings) < 2:
            print(f"   ⚠️ Insufficient readings")
            return False
        
        # Check interval changes
        intervals = []
        for i in range(1, len(readings)):
            interval = readings[i]['timestamp'] - readings[i-1]['timestamp']
            intervals.append(interval)
        
        avg_interval = sum(intervals) / len(intervals)
        baseline_interval = self.baseline_readings.get(sensor_id, {}).get('avg_interval', 1.0)
        
        interval_change = abs(avg_interval - baseline_interval)
        significant_change = interval_change > 0.2  # 200ms change is significant
        
        # Check if sensor stopped/started
        reading_rate = len(readings) / monitor_time
        baseline_rate = self.baseline_readings.get(sensor_id, {}).get('readings_count', 10) / 10
        rate_change = abs(reading_rate - baseline_rate)
        
        print(f"   📈 Results:")
        print(f"      Readings: {len(readings)} (rate: {reading_rate:.2f}/s)")
        print(f"      Avg interval: {avg_interval:.2f}s (baseline: {baseline_interval:.2f}s)")
        print(f"      Interval change: {interval_change:.2f}s")
        
        if significant_change:
            print(f"   🎉 SIGNIFICANT CHANGE DETECTED!")
            self.test_results.append({
                'sensor': sensor_id,
                'command': command_bytes,
                'description': description,
                'success': True,
                'interval_change': interval_change,
                'new_interval': avg_interval
            })
            return True
        elif rate_change > 1.0:
            print(f"   🎯 RATE CHANGE DETECTED!")
            self.test_results.append({
                'sensor': sensor_id,
                'command': command_bytes,
                'description': description,
                'success': True,
                'rate_change': rate_change
            })
            return True
        else:
            print(f"   ⚪ No significant change")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive control command discovery"""
        print("🔍 COMPREHENSIVE CONTROL DISCOVERY")
        print("=" * 40)
        
        if not self.controller.sensors:
            print("❌ No sensors found!")
            return
        
        # Get baseline
        self.get_baseline(duration=15)
        
        # Test different command categories
        command_categories = {
            "Toggle Commands": [
                [0x01, 0x81, 0x33, 0x01, 0x00, 0x00, 0x00, 0x00],  # Data query variant
                [0x01, 0x82, 0x33, 0x01, 0x00, 0x00, 0x00, 0x00],  # Another variant
                [0x01, 0x80, 0x34, 0x01, 0x00, 0x00, 0x00, 0x00],  # Modified data query
                [0x01, 0x80, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00],  # Toggle bit
                [0x01, 0x80, 0x33, 0x02, 0x00, 0x00, 0x00, 0x00],  # Different toggle
            ],
            
            "Firmware-based Commands": [
                [0x01, 0x86, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00],  # Firmware + control
                [0x01, 0x86, 0x02, 0x01, 0x00, 0x00, 0x00, 0x00],  # Different control
                [0x01, 0x86, 0x33, 0x01, 0x00, 0x00, 0x00, 0x00],  # Firmware + data
                [0x01, 0x86, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00],  # Modified firmware
            ],
            
            "Keyboard Simulation": [
                [0x01, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],  # Caps Lock
                [0x01, 0x53, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],  # Num Lock
                [0x01, 0x39, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00],  # Double Caps
                [0x01, 0x53, 0x53, 0x00, 0x00, 0x00, 0x00, 0x00],  # Double Num
            ],
            
            "Direct Control": [
                [0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],  # Simple on
                [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],  # Simple off
                [0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],  # Different header
                [0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],  # No header
            ],
            
            "Interval Commands": [
                [0x01, 0x80, 0x33, 0x01, 0x01, 0x00, 0x00, 0x00],  # 1 second
                [0x01, 0x80, 0x33, 0x01, 0x02, 0x00, 0x00, 0x00],  # 2 seconds
                [0x01, 0x80, 0x33, 0x01, 0x05, 0x00, 0x00, 0x00],  # 5 seconds
                [0x01, 0x80, 0x33, 0x01, 0x0A, 0x00, 0x00, 0x00],  # 10 seconds
            ]
        }
        
        # Test each category on each sensor
        for sensor_id in self.controller.sensors.keys():
            print(f"\n{'='*20} TESTING {sensor_id.upper()} {'='*20}")
            
            for category, commands in command_categories.items():
                print(f"\n📂 {category}:")
                
                for i, cmd in enumerate(commands):
                    success = self.test_control_command(
                        sensor_id, cmd, f"{category} #{i+1}", monitor_time=8
                    )
                    
                    if success:
                        print(f"   🎉 WORKING COMMAND FOUND!")
                        # Test it again to confirm
                        print(f"   🔄 Confirming...")
                        confirmed = self.test_control_command(
                            sensor_id, cmd, f"CONFIRMATION: {category} #{i+1}", monitor_time=8
                        )
                        if confirmed:
                            print(f"   ✅ CONFIRMED WORKING!")
                        else:
                            print(f"   ⚠️ Could not confirm")
                    
                    time.sleep(2)  # Pause between tests
        
        # Summary
        print(f"\n📋 DISCOVERY SUMMARY")
        print("=" * 25)
        
        if self.test_results:
            print(f"✅ Found {len(self.test_results)} working commands:")
            for result in self.test_results:
                print(f"  • {result['sensor']}: {result['description']}")
                print(f"    Command: {[hex(b) for b in result['command']]}")
                if 'interval_change' in result:
                    print(f"    Interval change: {result['interval_change']:.2f}s")
                if 'rate_change' in result:
                    print(f"    Rate change: {result['rate_change']:.2f}/s")
                print()
        else:
            print("❌ No working commands found")
            print("Possible reasons:")
            print("  1. Commands require different timing")
            print("  2. Need to send to different interface")
            print("  3. Require specific sequence of commands")
            print("  4. Linux driver interfering")

def main():
    if os.geteuid() != 0:
        print("❌ Need sudo for hidraw access")
        exit(1)
    
    discovery = ControlDiscovery(verbose=True)
    discovery.run_comprehensive_test()

if __name__ == "__main__":
    main()