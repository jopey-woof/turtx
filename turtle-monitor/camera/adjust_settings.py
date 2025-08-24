#!/usr/bin/env python3
"""
🐢 Camera Settings Adjustment Script
Direct camera settings adjustment for the Arducam USB camera
"""

import cv2
import time
import sys
import os

def adjust_camera_settings():
    """Adjust camera settings to fix washed out appearance"""
    
    print("🎥 Camera Settings Adjustment Tool")
    print("=" * 40)
    
    # Initialize camera
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("❌ Failed to open camera")
        return False
    
    print("✅ Camera opened successfully")
    
    # Current recommended settings for better image quality
    settings = {
        'brightness': 25,      # Reduced for less washed out appearance
        'contrast': 65,        # Increased for better definition
        'saturation': 55,      # Slightly increased for better colors
        'hue': 0,             # No hue adjustment
        'gain': 15,           # Reduced to minimize noise and brightness
        'exposure': -2,       # Slightly brighter than -3
        'focus': 0,           # Auto focus
        'white_balance': 5200, # Slightly warmer white balance
    }
    
    print("\n📊 Applying optimized settings:")
    for setting, value in settings.items():
        try:
            if setting == 'brightness':
                camera.set(cv2.CAP_PROP_BRIGHTNESS, value)
            elif setting == 'contrast':
                camera.set(cv2.CAP_PROP_CONTRAST, value)
            elif setting == 'saturation':
                camera.set(cv2.CAP_PROP_SATURATION, value)
            elif setting == 'hue':
                camera.set(cv2.CAP_PROP_HUE, value)
            elif setting == 'gain':
                camera.set(cv2.CAP_PROP_GAIN, value)
            elif setting == 'exposure':
                camera.set(cv2.CAP_PROP_EXPOSURE, value)
            elif setting == 'focus':
                camera.set(cv2.CAP_PROP_FOCUS, value)
            elif setting == 'white_balance':
                camera.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, value)
            
            print(f"  ✅ {setting}: {value}")
            
        except Exception as e:
            print(f"  ❌ {setting}: Failed to set {value} - {e}")
    
    # Test capture
    print("\n📸 Testing camera capture...")
    ret, frame = camera.read()
    
    if ret and frame is not None:
        # Save test image
        test_image_path = "/tmp/camera_test.jpg"
        cv2.imwrite(test_image_path, frame)
        
        # Get image info
        height, width, channels = frame.shape
        file_size = os.path.getsize(test_image_path)
        
        print(f"✅ Test capture successful!")
        print(f"   Resolution: {width}x{height}")
        print(f"   File size: {file_size} bytes")
        print(f"   Saved to: {test_image_path}")
        
        # Analyze image brightness
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_brightness = gray.mean()
        print(f"   Average brightness: {mean_brightness:.1f} (0-255)")
        
        if mean_brightness > 200:
            print("   ⚠️  Image still appears bright - consider reducing brightness further")
        elif mean_brightness < 100:
            print("   ⚠️  Image appears dark - consider increasing brightness")
        else:
            print("   ✅ Image brightness looks good")
            
    else:
        print("❌ Failed to capture test image")
    
    # Cleanup
    camera.release()
    print("\n🎯 Camera settings adjustment complete!")
    return True

def show_current_settings():
    """Show current camera settings"""
    
    print("🔍 Current Camera Settings")
    print("=" * 30)
    
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("❌ Failed to open camera")
        return False
    
    settings = [
        ('brightness', cv2.CAP_PROP_BRIGHTNESS),
        ('contrast', cv2.CAP_PROP_CONTRAST),
        ('saturation', cv2.CAP_PROP_SATURATION),
        ('hue', cv2.CAP_PROP_HUE),
        ('gain', cv2.CAP_PROP_GAIN),
        ('exposure', cv2.CAP_PROP_EXPOSURE),
        ('focus', cv2.CAP_PROP_FOCUS),
        ('white_balance', cv2.CAP_PROP_WHITE_BALANCE_BLUE_U),
    ]
    
    for name, prop in settings:
        try:
            value = camera.get(prop)
            print(f"  {name}: {value}")
        except Exception as e:
            print(f"  {name}: Error reading value - {e}")
    
    camera.release()
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        show_current_settings()
    else:
        adjust_camera_settings() 