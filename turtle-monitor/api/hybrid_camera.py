#!/usr/bin/env python3
"""
🐢 Hybrid Camera Solution
Combines FFmpeg for high-quality snapshots and OpenCV for streaming
"""

import cv2
import subprocess
import threading
import time
import os
import tempfile
from typing import Optional, Dict, Any
import logging
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class HybridCameraManager:
    """Hybrid camera manager using FFmpeg + OpenCV"""
    
    def __init__(self, device="/dev/video0", resolution=(1920, 1080), fps=30):
        self.device = device
        self.width, self.height = resolution
        self.fps = fps
        self.is_connected = False
        self.last_frame = None
        self.last_frame_time = 0
        
        # Camera settings
        self.settings = {
            'brightness': 25,
            'contrast': 65,
            'saturation': 55,
            'gain': 15,
            'auto_exposure': 1,
            'exposure_time': 156,
            'sharpness': 3,
            'white_balance_auto': 1
        }
        
        # OpenCV camera for streaming
        self.opencv_camera = None
        
        # Threading
        self.lock = threading.Lock()
        self.should_stop = False
        
        # Health monitoring
        self.health_data = {
            'last_check': None,
            'connection_status': 'disconnected',
            'frame_count': 0,
            'error_count': 0,
            'last_error': None,
            'uptime': 0,
            'fps_actual': 0,
            'capture_method': 'hybrid'
        }
        
        # Initialize
        self.init_camera()
    
    def check_ffmpeg_available(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def apply_camera_settings(self):
        """Apply camera settings using v4l2-ctl"""
        try:
            commands = [
                ['v4l2-ctl', '--device', self.device, '--set-ctrl', f'brightness={self.settings["brightness"]}'],
                ['v4l2-ctl', '--device', self.device, '--set-ctrl', f'contrast={self.settings["contrast"]}'],
                ['v4l2-ctl', '--device', self.device, '--set-ctrl', f'saturation={self.settings["saturation"]}'],
                ['v4l2-ctl', '--device', self.device, '--set-ctrl', f'gain={self.settings["gain"]}'],
                ['v4l2-ctl', '--device', self.device, '--set-ctrl', 'auto_exposure=1'],
                ['v4l2-ctl', '--device', self.device, '--set-ctrl', f'exposure_time_absolute={self.settings["exposure_time"]}'],
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    logger.warning(f"Failed to apply setting {cmd}: {result.stderr}")
                    
        except Exception as e:
            logger.error(f"Error applying camera settings: {e}")
    
    def init_camera(self) -> bool:
        """Initialize camera connection"""
        try:
            logger.info(f"🎥 Initializing hybrid camera at {self.device}")
            
            # Apply camera settings
            self.apply_camera_settings()
            
            # Initialize OpenCV camera for streaming
            self.opencv_camera = cv2.VideoCapture(self.device)
            
            if not self.opencv_camera.isOpened():
                logger.error(f"Failed to open camera with OpenCV")
                return False
            
            # Set OpenCV properties
            self.opencv_camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.opencv_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.opencv_camera.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Test capture
            ret, frame = self.opencv_camera.read()
            if not ret or frame is None:
                logger.error("Failed to capture test frame")
                self.opencv_camera.release()
                return False
            
            self.is_connected = True
            self.last_frame = frame
            self.last_frame_time = time.time()
            self.health_data['connection_status'] = 'connected'
            self.health_data['last_check'] = datetime.now()
            
            logger.info("✅ Hybrid camera initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Camera initialization failed: {e}")
            self.health_data['last_error'] = str(e)
            self.health_data['error_count'] += 1
            return False
    
    def get_ffmpeg_snapshot(self) -> Optional[bytes]:
        """Get high-quality snapshot using FFmpeg"""
        try:
            if not self.check_ffmpeg_available():
                logger.warning("FFmpeg not available, falling back to OpenCV")
                return self.get_opencv_snapshot()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                temp_path = tmp_file.name
            
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
                    temp_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and os.path.exists(temp_path):
                    with open(temp_path, 'rb') as f:
                        image_data = f.read()
                    
                    file_size = len(image_data)
                    logger.info(f"FFmpeg snapshot captured: {file_size} bytes")
                    return image_data
                else:
                    # Check if it's a device busy error
                    if "Device or resource busy" in result.stderr or "busy" in result.stderr.lower():
                        logger.warning("Camera device busy, falling back to OpenCV snapshot")
                        return self.get_opencv_snapshot()
                    else:
                        logger.error(f"FFmpeg snapshot failed: {result.stderr}")
                        return self.get_opencv_snapshot()
                    
            finally:
                # Cleanup temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error getting FFmpeg snapshot: {e}")
            return self.get_opencv_snapshot()
    
    def get_opencv_snapshot(self) -> Optional[bytes]:
        """Get snapshot using OpenCV"""
        try:
            frame = self.get_opencv_frame()
            if frame is None:
                return None
            
            # Encode as JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
            ret, jpeg_data = cv2.imencode('.jpg', frame, encode_param)
            
            if not ret:
                logger.error("Failed to encode JPEG")
                return None
            
            return jpeg_data.tobytes()
            
        except Exception as e:
            logger.error(f"Error getting OpenCV snapshot: {e}")
            return None
    
    def get_opencv_frame(self) -> Optional[np.ndarray]:
        """Get frame from OpenCV camera"""
        try:
            with self.lock:
                if not self.opencv_camera or not self.opencv_camera.isOpened():
                    return None
                
                ret, frame = self.opencv_camera.read()
                if not ret or frame is None:
                    logger.warning("Failed to capture OpenCV frame")
                    return None
                
                # Update frame data
                self.last_frame = frame
                self.last_frame_time = time.time()
                self.health_data['frame_count'] += 1
                
                return frame
                
        except Exception as e:
            logger.error(f"Error getting OpenCV frame: {e}")
            self.health_data['last_error'] = str(e)
            self.health_data['error_count'] += 1
            return None
    
    def get_stream_frame(self) -> Optional[bytes]:
        """Get frame for MJPEG streaming (using OpenCV)"""
        try:
            frame = self.get_opencv_frame()
            if frame is None:
                return None
            
            # Resize for streaming if needed
            if frame.shape[1] > 1280:  # Resize if width > 1280
                scale = 1280 / frame.shape[1]
                new_width = int(frame.shape[1] * scale)
                new_height = int(frame.shape[0] * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # Encode as JPEG for streaming
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]  # Lower quality for streaming
            ret, jpeg_data = cv2.imencode('.jpg', frame, encode_param)
            
            if not ret:
                logger.error("Failed to encode stream frame")
                return None
            
            return jpeg_data.tobytes()
            
        except Exception as e:
            logger.error(f"Error getting stream frame: {e}")
            return None
    
    def check_health(self) -> Dict[str, Any]:
        """Check camera health and return status"""
        try:
            current_time = time.time()
            
            # Update uptime
            if self.health_data['last_check']:
                self.health_data['uptime'] = current_time - self.health_data['last_check'].timestamp()
            
            # Check if camera is still connected
            is_connected = (self.opencv_camera is not None and 
                          self.opencv_camera.isOpened())
            
            # Calculate FPS
            if self.last_frame_time > 0:
                time_diff = current_time - self.last_frame_time
                if time_diff > 0:
                    self.health_data['fps_actual'] = 1.0 / time_diff
            
            # Update connection status
            self.health_data['connection_status'] = 'connected' if is_connected else 'disconnected'
            self.health_data['last_check'] = datetime.now()
            
            return {
                'connected': bool(is_connected),
                'device': self.device,
                'resolution': f"{self.width}x{self.height}",
                'fps_target': int(self.fps),
                'fps_actual': float(self.health_data.get('fps_actual', 0)),
                'capture_method': str(self.health_data.get('capture_method', 'hybrid')),
                'uptime': float(self.health_data.get('uptime', 0)),
                'frame_count': int(self.health_data.get('frame_count', 0)),
                'error_count': int(self.health_data.get('error_count', 0)),
                'last_error': self.health_data.get('last_error'),
                'last_check': self.health_data.get('last_check'),
                'connection_status': str(self.health_data.get('connection_status', 'unknown'))
            }
            
        except Exception as e:
            logger.error(f"Error checking health: {e}")
            return {
                'connected': False,
                'error': str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive camera status"""
        health = self.check_health()
        
        # Convert numpy types to Python native types for JSON serialization
        def convert_numpy_types(obj):
            if hasattr(obj, 'item'):  # numpy scalar
                return obj.item()
            elif isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(v) for v in obj]
            else:
                return obj
        
        status = {
            "connected": bool(self.is_connected),
            "device": self.device,
            "resolution": f"{self.width}x{self.height}",
            "fps_target": int(self.fps),
            "fps_actual": float(health.get('fps_actual', 0)),
            "capture_method": str(health.get('capture_method', 'hybrid')),
            "quality": 85,
            "uptime": float(health.get('uptime', 0)),
            "frame_count": int(health.get('frame_count', 0)),
            "error_count": int(health.get('error_count', 0)),
            "last_error": health.get('last_error'),
            "last_check": health.get('last_check'),
            "connection_status": str(health.get('connection_status', 'unknown'))
        }
        
        return convert_numpy_types(status)
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """Update camera settings"""
        self.settings.update(new_settings)
        self.apply_camera_settings()
        logger.info(f"Camera settings updated: {new_settings}")
    
    def restart(self):
        """Restart camera connection"""
        try:
            logger.info("🔄 Restarting hybrid camera")
            
            # Stop current camera
            if self.opencv_camera:
                self.opencv_camera.release()
            
            # Reinitialize
            self.is_connected = False
            time.sleep(1)
            
            success = self.init_camera()
            if success:
                logger.info("✅ Camera restart successful")
            else:
                logger.error("❌ Camera restart failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error restarting camera: {e}")
            return False
    
    def stop(self):
        """Stop camera and cleanup"""
        self.should_stop = True
        
        if self.opencv_camera:
            self.opencv_camera.release()
        
        logger.info("Hybrid camera stopped")

# Example usage
if __name__ == "__main__":
    # Test hybrid camera
    camera = HybridCameraManager()
    
    if camera.is_connected:
        print("✅ Hybrid camera connected")
        
        # Test FFmpeg snapshot
        snapshot_data = camera.get_ffmpeg_snapshot()
        if snapshot_data:
            print(f"✅ FFmpeg snapshot: {len(snapshot_data)} bytes")
            
            # Save test image
            with open('/tmp/hybrid_test_snapshot.jpg', 'wb') as f:
                f.write(snapshot_data)
            print("Test image saved to /tmp/hybrid_test_snapshot.jpg")
        
        # Test OpenCV frame
        frame = camera.get_opencv_frame()
        if frame is not None:
            print(f"✅ OpenCV frame: {frame.shape}")
        
        # Get status
        status = camera.get_status()
        print("Camera status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
    else:
        print("❌ Hybrid camera failed to connect")
    
    camera.stop() 