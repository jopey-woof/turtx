#!/usr/bin/env python3
"""
File Capture Demo for TEMPerHUM Sensors
======================================

This script demonstrates how to capture TEMPerHUM sensor output to files
without terminal interference.

Usage:
    python3 demo_file_capture.py
"""

import os
import sys
import time
import subprocess
from datetime import datetime

def create_simple_capture():
    """Create a simple capture script."""
    script_content = '''#!/usr/bin/env python3
import sys
from datetime import datetime

# Create output file with timestamp
output_file = f"/tmp/temperhum_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

print(f"🐢 TEMPerHUM File Capture Demo")
print(f"📁 Capturing to: {output_file}")
print("")
print("Instructions:")
print("1. Press TXT button on sensors or hold Num Lock for 3 seconds")
print("2. Watch data being captured to the file")
print("3. Press Ctrl+C to stop")
print("")

try:
    with open(output_file, 'w') as f:
        f.write(f"Capture started at {datetime.now()}\\n")
        f.write("=" * 50 + "\\n")
        
        line_count = 0
        while True:
            try:
                line = input().strip()
                line_count += 1
                
                # Write to file with timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%3N')
                f.write(f"{timestamp}: {line}\\n")
                f.flush()  # Ensure data is written immediately
                
                # Show progress
                print(f"📥 Line {line_count}: {line}")
                
            except EOFError:
                break
                
except KeyboardInterrupt:
    print("\\n⏹️ Capture stopped by user")
    print(f"📁 Data saved to: {output_file}")
    print(f"📊 Total lines captured: {line_count}")
'''

    script_path = "/tmp/demo_capture.py"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    os.chmod(script_path, 0o755)
    return script_path

def main():
    """Main demonstration function."""
    print("🐢 TEMPerHUM File Capture Demo")
    print("=" * 50)
    
    print("This demo shows how to capture sensor output to files")
    print("without terminal interference.")
    print("")
    
    # Create the demo capture script
    script_path = create_simple_capture()
    
    print("✅ Demo capture script created!")
    print("")
    print("📋 STEP-BY-STEP INSTRUCTIONS:")
    print("")
    print("1. Open a NEW terminal window/tab")
    print("2. Run this command:")
    print(f"   python3 {script_path}")
    print("")
    print("3. In that terminal, you'll see:")
    print("   - Capture instructions")
    print("   - File location")
    print("   - Real-time capture progress")
    print("")
    print("4. Activate your sensors:")
    print("   - Press TXT button on sensors, OR")
    print("   - Hold Num Lock for 3 seconds")
    print("")
    print("5. Watch the data being captured:")
    print("   - Each line shows: '📥 Line X: [sensor data]'")
    print("   - Data is automatically saved to file")
    print("")
    print("6. Stop capture with Ctrl+C")
    print("")
    print("7. Check the captured file:")
    print("   - Raw data with timestamps")
    print("   - Ready for parsing and analysis")
    print("")
    
    # Show example of what the output looks like
    print("📊 EXAMPLE OUTPUT:")
    print("🐢 TEMPerHUM File Capture Demo")
    print("📁 Capturing to: /tmp/temperhum_demo_20250821_174500.txt")
    print("")
    print("Instructions:")
    print("1. Press TXT button on sensors or hold Num Lock for 3 seconds")
    print("2. Watch data being captured to the file")
    print("3. Press Ctrl+C to stop")
    print("")
    print("📥 Line 1: www.pcsensor.com")
    print("📥 Line 2: temperhum v4.1")
    print("📥 Line 3: 28.34 [c] 36.42 [%rh] 1s")
    print("📥 Line 4: 28.31 [c] 36.37 [%rh] 1s")
    print("📥 Line 5: 28.35 [c] 36.33 [%rh] 1s")
    print("...")
    print("")
    print("⏹️ Capture stopped by user")
    print("📁 Data saved to: /tmp/temperhum_demo_20250821_174500.txt")
    print("📊 Total lines captured: 15")
    print("")
    
    print("💡 ADVANTAGES OF FILE CAPTURE:")
    print("✅ No terminal interference")
    print("✅ Scripts can run independently")
    print("✅ Data is preserved with timestamps")
    print("✅ Easy to parse and analyze later")
    print("✅ Works for both local and remote deployment")
    print("")
    
    print("🚀 READY FOR REMOTE DEPLOYMENT:")
    print("This same method works perfectly on the remote machine!")
    print("Just copy the script and run it via SSH.")
    print("")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 