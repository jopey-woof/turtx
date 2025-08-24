#!/usr/bin/env python3
"""
🐢 Advanced Camera Adjustment Tool
Comprehensive camera optimization for Arducam USB camera
Tests multiple capture methods and finds optimal settings
"""

import cv2
import subprocess
import time
import os
import sys
import json
from datetime import datetime

class AdvancedCameraAdjuster:
    def __init__(self):
        self.device = "/dev/video0"
        self.test_results = {}
        
    def check_system_capabilities(self):
        """Check what video capture tools are available"""
        print("🔍 Checking System Capabilities")
        print("=" * 40)
        
        tools = {
            'ffmpeg': 'FFmpeg video capture',
            'v4l2-ctl': 'V4L2 control utility',
            'v4l2-ctl': 'V4L2 control utility',
            'gst-launch-1.0': 'GStreamer pipeline'
        }
        
        available_tools = {}
        for tool, description in tools.items():
            try:
                result = subprocess.run([tool, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    available_tools[tool] = description
                    print(f"✅ {tool}: {description}")
                else:
                    print(f"❌ {tool}: Not available")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print(f"❌ {tool}: Not available")
        
        return available_tools
    
    def get_camera_info(self):
        """Get detailed camera information"""
        print("\n📹 Camera Information")
        print("=" * 30)
        
        try:
            # Get camera capabilities
            result = subprocess.run(['v4l2-ctl', '--device', self.device, '--list-formats-ext'],
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("Camera Formats:")
                print(result.stdout)
            else:
                print("❌ Could not get camera formats")
                
        except Exception as e:
            print(f"❌ Error getting camera info: {e}")
    
    def test_opencv_capture(self):
        """Test OpenCV capture with different settings"""
        print("\n🎥 Testing OpenCV Capture")
        print("=" * 30)
        
        camera = cv2.VideoCapture(self.device)
        if not camera.isOpened():
            print("❌ Failed to open camera with OpenCV")
            return False
        
        # Test different resolutions
        resolutions = [
            (640, 480),
            (1280, 720),
            (1920, 1080)
        ]
        
        for width, height in resolutions:
            print(f"\nTesting resolution: {width}x{height}")
            
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Get actual resolution
            actual_width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            
            print(f"  Requested: {width}x{height}")
            print(f"  Actual: {actual_width:.0f}x{actual_height:.0f}")
            
            # Test capture
            ret, frame = camera.read()
            if ret and frame is not None:
                frame_height, frame_width = frame.shape[:2]
                print(f"  Captured: {frame_width}x{frame_height}")
                
                # Save test image
                filename = f"/tmp/opencv_test_{width}x{height}.jpg"
                cv2.imwrite(filename, frame)
                file_size = os.path.getsize(filename)
                print(f"  File size: {file_size} bytes")
                
                # Analyze quality
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                mean_brightness = gray.mean()
                std_dev = gray.std()
                print(f"  Brightness: {mean_brightness:.1f} (0-255)")
                print(f"  Contrast: {std_dev:.1f}")
                
            else:
                print("  ❌ Failed to capture frame")
        
        camera.release()
        return True
    
    def test_ffmpeg_capture(self):
        """Test FFmpeg capture for better quality"""
        print("\n🎬 Testing FFmpeg Capture")
        print("=" * 30)
        
        try:
            # Test FFmpeg capture
            cmd = [
                'ffmpeg', '-f', 'v4l2', '-i', self.device,
                '-vframes', '1', '-y', '/tmp/ffmpeg_test.jpg'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists('/tmp/ffmpeg_test.jpg'):
                file_size = os.path.getsize('/tmp/ffmpeg_test.jpg')
                print(f"✅ FFmpeg capture successful")
                print(f"  File size: {file_size} bytes")
                
                # Compare with OpenCV
                if os.path.exists('/tmp/opencv_test_1920x1080.jpg'):
                    opencv_size = os.path.getsize('/tmp/opencv_test_1920x1080.jpg')
                    improvement = (file_size / opencv_size - 1) * 100
                    print(f"  vs OpenCV: {improvement:+.1f}% size difference")
                
                return True
            else:
                print(f"❌ FFmpeg capture failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ FFmpeg test error: {e}")
            return False
    
    def test_gstreamer_capture(self):
        """Test GStreamer capture pipeline"""
        print("\n🎭 Testing GStreamer Capture")
        print("=" * 30)
        
        try:
            # GStreamer pipeline for high quality capture
            pipeline = (
                f'v4l2src device={self.device} ! '
                'video/x-raw,width=1920,height=1080,framerate=30/1 ! '
                'videoconvert ! '
                'jpegenc quality=95 ! '
                'multifilesink location=/tmp/gstreamer_test.jpg'
            )
            
            cmd = ['gst-launch-1.0', '-e', pipeline]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists('/tmp/gstreamer_test.jpg'):
                file_size = os.path.getsize('/tmp/gstreamer_test.jpg')
                print(f"✅ GStreamer capture successful")
                print(f"  File size: {file_size} bytes")
                return True
            else:
                print(f"❌ GStreamer capture failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ GStreamer test error: {e}")
            return False
    
    def optimize_camera_settings(self):
        """Find optimal camera settings"""
        print("\n⚙️ Optimizing Camera Settings")
        print("=" * 35)
        
        camera = cv2.VideoCapture(self.device)
        if not camera.isOpened():
            print("❌ Failed to open camera")
            return False
        
        # Test different setting combinations
        test_settings = [
            {'brightness': 20, 'contrast': 70, 'gain': 10, 'exposure': -1},
            {'brightness': 25, 'contrast': 65, 'gain': 15, 'exposure': -2},
            {'brightness': 30, 'contrast': 60, 'gain': 20, 'exposure': -3},
            {'brightness': 15, 'contrast': 75, 'gain': 5, 'exposure': 0},
            {'brightness': 35, 'contrast': 55, 'gain': 25, 'exposure': -4},
        ]
        
        best_settings = None
        best_score = 0
        
        for i, settings in enumerate(test_settings):
            print(f"\nTest {i+1}: {settings}")
            
            # Apply settings
            for setting, value in settings.items():
                if setting == 'brightness':
                    camera.set(cv2.CAP_PROP_BRIGHTNESS, value)
                elif setting == 'contrast':
                    camera.set(cv2.CAP_PROP_CONTRAST, value)
                elif setting == 'gain':
                    camera.set(cv2.CAP_PROP_GAIN, value)
                elif setting == 'exposure':
                    camera.set(cv2.CAP_PROP_EXPOSURE, value)
            
            # Wait for settings to apply
            time.sleep(1)
            
            # Capture and analyze
            ret, frame = camera.read()
            if ret and frame is not None:
                # Save test image
                filename = f"/tmp/optimization_test_{i+1}.jpg"
                cv2.imwrite(filename, frame)
                file_size = os.path.getsize(filename)
                
                # Analyze quality
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                mean_brightness = gray.mean()
                std_dev = gray.std()
                
                # Calculate quality score (higher is better)
                # Penalize over-brightness and under-brightness
                brightness_score = 255 - abs(mean_brightness - 128)
                contrast_score = std_dev
                size_score = min(file_size / 1000, 100)  # Cap at 100KB
                
                total_score = brightness_score + contrast_score + size_score
                
                print(f"  Brightness: {mean_brightness:.1f}")
                print(f"  Contrast: {std_dev:.1f}")
                print(f"  File size: {file_size} bytes")
                print(f"  Quality score: {total_score:.1f}")
                
                if total_score > best_score:
                    best_score = total_score
                    best_settings = settings.copy()
                    print(f"  🏆 New best settings!")
            else:
                print("  ❌ Failed to capture frame")
        
        camera.release()
        
        if best_settings:
            print(f"\n🎯 Best Settings Found:")
            print(f"  {best_settings}")
            print(f"  Quality score: {best_score:.1f}")
            
            # Save best settings
            with open('/tmp/best_camera_settings.json', 'w') as f:
                json.dump(best_settings, f, indent=2)
            
            return best_settings
        
        return None
    
    def generate_optimized_config(self, best_settings):
        """Generate optimized configuration files"""
        print("\n📝 Generating Optimized Configuration")
        print("=" * 40)
        
        if not best_settings:
            print("❌ No best settings found")
            return
        
        # Generate Python config
        python_config = f'''# Optimized Camera Settings for Arducam USB Camera
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OPTIMAL_CAMERA_SETTINGS = {best_settings}

# Usage in camera.py:
# self.camera_settings = OPTIMAL_CAMERA_SETTINGS.copy()
'''
        
        with open('/tmp/optimized_camera_config.py', 'w') as f:
            f.write(python_config)
        
        # Generate v4l2-ctl commands
        v4l2_commands = f'''# v4l2-ctl commands to apply optimal settings
# Run these commands to set camera settings:

v4l2-ctl --device {self.device} --set-ctrl brightness={best_settings.get('brightness', 25)}
v4l2-ctl --device {self.device} --set-ctrl contrast={best_settings.get('contrast', 65)}
v4l2-ctl --device {self.device} --set-ctrl gain={best_settings.get('gain', 15)}
v4l2-ctl --device {self.device} --set-ctrl exposure_auto=1
v4l2-ctl --device {self.device} --set-ctrl exposure_absolute={best_settings.get('exposure', -2)}
'''
        
        with open('/tmp/apply_optimal_settings.sh', 'w') as f:
            f.write(v4l2_commands)
        
        # Make script executable
        os.chmod('/tmp/apply_optimal_settings.sh', 0o755)
        
        print("✅ Generated configuration files:")
        print("  /tmp/optimized_camera_config.py")
        print("  /tmp/apply_optimal_settings.sh")
        print("  /tmp/best_camera_settings.json")
    
    def run_comprehensive_test(self):
        """Run comprehensive camera optimization"""
        print("🐢 Advanced Camera Optimization Tool")
        print("=" * 50)
        print(f"Device: {self.device}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check system capabilities
        available_tools = self.check_system_capabilities()
        
        # Get camera information
        self.get_camera_info()
        
        # Test different capture methods
        opencv_ok = self.test_opencv_capture()
        
        if 'ffmpeg' in available_tools:
            ffmpeg_ok = self.test_ffmpeg_capture()
        else:
            ffmpeg_ok = False
        
        if 'gst-launch-1.0' in available_tools:
            gstreamer_ok = self.test_gstreamer_capture()
        else:
            gstreamer_ok = False
        
        # Optimize settings
        best_settings = self.optimize_camera_settings()
        
        # Generate configuration
        self.generate_optimized_config(best_settings)
        
        # Summary
        print("\n📊 Test Summary")
        print("=" * 20)
        print(f"OpenCV: {'✅' if opencv_ok else '❌'}")
        print(f"FFmpeg: {'✅' if ffmpeg_ok else '❌'}")
        print(f"GStreamer: {'✅' if gstreamer_ok else '❌'}")
        
        if best_settings:
            print(f"Best Settings: {best_settings}")
        
        print("\n🎯 Next Steps:")
        print("1. Review the generated configuration files")
        print("2. Apply the optimal settings to your camera")
        print("3. Test the camera with the new settings")
        print("4. Update your camera.py with the optimal configuration")

def main():
    adjuster = AdvancedCameraAdjuster()
    adjuster.run_comprehensive_test()

if __name__ == "__main__":
    main() 