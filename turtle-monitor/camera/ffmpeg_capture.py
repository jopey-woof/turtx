#!/usr/bin/env python3
"""
🐢 High-Quality FFmpeg Camera Capture
Alternative to OpenCV for better image quality with Arducam USB camera
"""

import subprocess
import threading
import time
import os
import signal
import tempfile
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FFmpegCameraCapture:
    """High-quality camera capture using FFmpeg"""
    
    def __init__(self, device="/dev/video0", resolution=(1920, 1080), fps=30):
        self.device = device
        self.width, self.height = resolution
        self.fps = fps
        self.process = None
        self.is_running = False
        self.temp_dir = tempfile.mkdtemp(prefix="ffmpeg_camera_")
        self.current_frame_path = os.path.join(self.temp_dir, "current_frame.jpg")
        self.stream_pipe = None
        
        # Camera settings
        self.settings = {
            'brightness': 25,
            'contrast': 65,
            'saturation': 55,
            'gain': 15,
            'exposure': -2,
            'white_balance': 5200
        }
    
    def check_ffmpeg_available(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_camera_formats(self) -> Dict[str, Any]:
        """Get available camera formats using v4l2-ctl"""
        try:
            result = subprocess.run([
                'v4l2-ctl', '--device', self.device, '--list-formats-ext'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return {'success': True, 'formats': result.stdout}
            else:
                return {'success': False, 'error': result.stderr}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def apply_camera_settings(self):
        """Apply camera settings using v4l2-ctl"""
        try:
            commands = [
                ['v4l2-ctl', '--device', self.device, '--set-ctrl', f'brightness={self.settings["brightness"]}'],
                ['v4l2-ctl', '--device', self.device, '--set-ctrl', f'contrast={self.settings["contrast"]}'],
                ['v4l2-ctl', '--device', self.device, '--set-ctrl', f'saturation={self.settings["saturation"]}'],
                ['v4l2-ctl', '--device', self.device, '--set-ctrl', f'gain={self.settings["gain"]}'],
                ['v4l2-ctl', '--device', self.device, '--set-ctrl', 'exposure_auto=1'],
                ['v4l2-ctl', '--device', self.device, '--set-ctrl', f'exposure_absolute={self.settings["exposure"]}'],
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    logger.warning(f"Failed to apply setting {cmd}: {result.stderr}")
                    
        except Exception as e:
            logger.error(f"Error applying camera settings: {e}")
    
    def capture_snapshot(self, output_path: Optional[str] = None) -> Optional[str]:
        """Capture a high-quality snapshot using FFmpeg"""
        if not output_path:
            output_path = self.current_frame_path
        
        try:
            # FFmpeg command for high-quality capture
            cmd = [
                'ffmpeg',
                '-f', 'v4l2',
                '-i', self.device,
                '-vframes', '1',
                '-vf', f'scale={self.width}:{self.height}',
                '-q:v', '2',  # High quality
                '-y',  # Overwrite output
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"Snapshot captured: {file_size} bytes")
                return output_path
            else:
                logger.error(f"FFmpeg snapshot failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error capturing snapshot: {e}")
            return None
    
    def start_mjpeg_stream(self, output_url: str = "http://localhost:8080/stream.mjpg"):
        """Start MJPEG stream using FFmpeg"""
        try:
            # FFmpeg command for MJPEG stream
            cmd = [
                'ffmpeg',
                '-f', 'v4l2',
                '-i', self.device,
                '-vf', f'scale={self.width}:{self.height}',
                '-r', str(self.fps),
                '-q:v', '3',  # Good quality for streaming
                '-f', 'mjpeg',
                'pipe:1'
            ]
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.is_running = True
            logger.info("FFmpeg MJPEG stream started")
            
        except Exception as e:
            logger.error(f"Error starting FFmpeg stream: {e}")
            self.is_running = False
    
    def start_rtsp_stream(self, rtsp_url: str = "rtsp://localhost:8554/turtle"):
        """Start RTSP stream using FFmpeg"""
        try:
            # FFmpeg command for RTSP stream
            cmd = [
                'ffmpeg',
                '-f', 'v4l2',
                '-i', self.device,
                '-vf', f'scale={self.width}:{self.height}',
                '-r', str(self.fps),
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-tune', 'zerolatency',
                '-f', 'rtsp',
                '-rtsp_transport', 'tcp',
                rtsp_url
            ]
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.is_running = True
            logger.info(f"FFmpeg RTSP stream started: {rtsp_url}")
            
        except Exception as e:
            logger.error(f"Error starting RTSP stream: {e}")
            self.is_running = False
    
    def get_frame_data(self) -> Optional[bytes]:
        """Get current frame as bytes"""
        try:
            if self.capture_snapshot():
                with open(self.current_frame_path, 'rb') as f:
                    return f.read()
            return None
        except Exception as e:
            logger.error(f"Error getting frame data: {e}")
            return None
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """Update camera settings"""
        self.settings.update(new_settings)
        self.apply_camera_settings()
        logger.info(f"Camera settings updated: {new_settings}")
    
    def stop(self):
        """Stop FFmpeg process and cleanup"""
        self.is_running = False
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            except Exception as e:
                logger.error(f"Error stopping FFmpeg process: {e}")
        
        # Cleanup temp files
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            logger.error(f"Error cleaning up temp directory: {e}")
        
        logger.info("FFmpeg camera capture stopped")

class FFmpegCameraManager:
    """Manager for FFmpeg-based camera operations"""
    
    def __init__(self, device="/dev/video0"):
        self.device = device
        self.capture = FFmpegCameraCapture(device)
        self.is_available = self.capture.check_ffmpeg_available()
        
        if not self.is_available:
            logger.warning("FFmpeg not available, falling back to OpenCV")
    
    def get_snapshot(self) -> Optional[bytes]:
        """Get camera snapshot"""
        if self.is_available:
            return self.capture.get_frame_data()
        return None
    
    def get_stream_frame(self) -> Optional[bytes]:
        """Get frame for streaming"""
        if self.is_available:
            return self.capture.get_frame_data()
        return None
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update camera settings"""
        if self.is_available:
            self.capture.update_settings(settings)
    
    def get_status(self) -> Dict[str, Any]:
        """Get camera status"""
        return {
            'ffmpeg_available': self.is_available,
            'device': self.device,
            'is_running': self.capture.is_running,
            'settings': self.capture.settings
        }
    
    def stop(self):
        """Stop camera manager"""
        self.capture.stop()

# Example usage
if __name__ == "__main__":
    # Test FFmpeg camera capture
    manager = FFmpegCameraManager()
    
    if manager.is_available:
        print("✅ FFmpeg camera capture available")
        
        # Get camera formats
        formats = manager.capture.get_camera_formats()
        if formats['success']:
            print("Camera formats:")
            print(formats['formats'])
        
        # Capture test snapshot
        snapshot_data = manager.get_snapshot()
        if snapshot_data:
            print(f"✅ Snapshot captured: {len(snapshot_data)} bytes")
            
            # Save test image
            with open('/tmp/ffmpeg_test_snapshot.jpg', 'wb') as f:
                f.write(snapshot_data)
            print("Test image saved to /tmp/ffmpeg_test_snapshot.jpg")
        else:
            print("❌ Failed to capture snapshot")
    else:
        print("❌ FFmpeg not available")
    
    manager.stop() 