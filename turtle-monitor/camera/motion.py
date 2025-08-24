#!/usr/bin/env python3
"""
🐢 Turtle Monitor Motion Detection
Motion detection for turtle activity monitoring
"""

import cv2
import numpy as np
import time
import logging
from typing import Optional, Tuple, List
from datetime import datetime

logger = logging.getLogger(__name__)

class MotionDetector:
    """Motion detection for turtle monitoring"""
    
    def __init__(self):
        self.prev_frame = None
        self.motion_threshold = 25  # Minimum change to detect motion
        self.min_motion_area = 500  # Minimum area to consider motion
        self.motion_history = []
        self.max_history = 100
        self.last_motion_time = None
        self.motion_cooldown = 5.0  # Seconds between motion events
        
        # Motion detection settings
        self.gaussian_blur_size = (21, 21)
        self.dilation_kernel = np.ones((5, 5), np.uint8)
        
        # Turtle-specific detection zones
        self.detection_zones = [
            # Basking area (top left)
            {'name': 'basking', 'roi': (0, 0, 0.4, 0.4)},
            # Water area (bottom center)
            {'name': 'water', 'roi': (0.3, 0.6, 0.4, 0.4)},
            # Feeding area (top right)
            {'name': 'feeding', 'roi': (0.6, 0, 0.4, 0.4)}
        ]
        
        logger.info("Motion detector initialized")
    
    def detect_motion(self, frame: np.ndarray) -> Optional[dict]:
        """Detect motion in the frame"""
        try:
            if frame is None:
                return None
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, self.gaussian_blur_size, 0)
            
            # Initialize previous frame
            if self.prev_frame is None:
                self.prev_frame = gray
                return None
            
            # Calculate frame difference
            frame_delta = cv2.absdiff(self.prev_frame, gray)
            thresh = cv2.threshold(frame_delta, self.motion_threshold, 255, cv2.THRESH_BINARY)[1]
            
            # Dilate to fill in holes
            thresh = cv2.dilate(thresh, self.dilation_kernel, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by area
            motion_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > self.min_motion_area:
                    motion_contours.append(contour)
            
            # Update previous frame
            self.prev_frame = gray
            
            # Check motion cooldown
            current_time = time.time()
            if (self.last_motion_time and 
                current_time - self.last_motion_time < self.motion_cooldown):
                return None
            
            if motion_contours:
                # Motion detected
                self.last_motion_time = current_time
                
                # Analyze motion zones
                zone_analysis = self.analyze_motion_zones(frame, motion_contours)
                
                # Calculate overall motion metrics
                total_area = sum(cv2.contourArea(c) for c in motion_contours)
                motion_center = self.calculate_motion_center(motion_contours, frame.shape)
                
                motion_data = {
                    'timestamp': datetime.now().isoformat(),
                    'motion_detected': True,
                    'total_area': total_area,
                    'contour_count': len(motion_contours),
                    'motion_center': motion_center,
                    'zones': zone_analysis,
                    'frame_shape': frame.shape[:2]
                }
                
                # Add to history
                self.motion_history.append(motion_data)
                if len(self.motion_history) > self.max_history:
                    self.motion_history.pop(0)
                
                logger.info(f"Motion detected: {len(motion_contours)} contours, "
                          f"total area: {total_area}, zones: {zone_analysis}")
                
                return motion_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error in motion detection: {e}")
            return None
    
    def analyze_motion_zones(self, frame: np.ndarray, contours: List) -> dict:
        """Analyze motion in different zones"""
        try:
            frame_height, frame_width = frame.shape[:2]
            zone_results = {}
            
            for zone in self.detection_zones:
                zone_name = zone['name']
                roi = zone['roi']
                
                # Calculate zone boundaries
                x1 = int(roi[0] * frame_width)
                y1 = int(roi[1] * frame_height)
                x2 = int((roi[0] + roi[2]) * frame_width)
                y2 = int((roi[1] + roi[3]) * frame_height)
                
                # Check which contours are in this zone
                zone_contours = []
                zone_area = 0
                
                for contour in contours:
                    # Get contour center
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        
                        # Check if center is in zone
                        if x1 <= cx <= x2 and y1 <= cy <= y2:
                            zone_contours.append(contour)
                            zone_area += cv2.contourArea(contour)
                
                zone_results[zone_name] = {
                    'motion_detected': len(zone_contours) > 0,
                    'contour_count': len(zone_contours),
                    'total_area': zone_area,
                    'zone_bounds': (x1, y1, x2, y2)
                }
            
            return zone_results
            
        except Exception as e:
            logger.error(f"Error analyzing motion zones: {e}")
            return {}
    
    def calculate_motion_center(self, contours: List, frame_shape: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Calculate the center of all motion"""
        try:
            if not contours:
                return None
            
            # Calculate weighted center based on contour areas
            total_moment_x = 0
            total_moment_y = 0
            total_area = 0
            
            for contour in contours:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    area = cv2.contourArea(contour)
                    total_moment_x += M["m10"] * area
                    total_moment_y += M["m01"] * area
                    total_area += area
            
            if total_area > 0:
                center_x = int(total_moment_x / total_area)
                center_y = int(total_moment_y / total_area)
                return (center_x, center_y)
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating motion center: {e}")
            return None
    
    def get_motion_history(self, minutes: int = 5) -> List[dict]:
        """Get motion history for the last N minutes"""
        try:
            cutoff_time = time.time() - (minutes * 60)
            recent_motion = []
            
            for motion in self.motion_history:
                motion_time = datetime.fromisoformat(motion['timestamp']).timestamp()
                if motion_time > cutoff_time:
                    recent_motion.append(motion)
            
            return recent_motion
            
        except Exception as e:
            logger.error(f"Error getting motion history: {e}")
            return []
    
    def get_motion_statistics(self, minutes: int = 5) -> dict:
        """Get motion statistics for the last N minutes"""
        try:
            recent_motion = self.get_motion_history(minutes)
            
            if not recent_motion:
                return {
                    'total_events': 0,
                    'average_area': 0,
                    'most_active_zone': None,
                    'motion_frequency': 0
                }
            
            # Calculate statistics
            total_events = len(recent_motion)
            total_area = sum(m['total_area'] for m in recent_motion)
            average_area = total_area / total_events
            
            # Find most active zone
            zone_activity = {}
            for motion in recent_motion:
                for zone_name, zone_data in motion['zones'].items():
                    if zone_data['motion_detected']:
                        zone_activity[zone_name] = zone_activity.get(zone_name, 0) + 1
            
            most_active_zone = max(zone_activity.items(), key=lambda x: x[1])[0] if zone_activity else None
            
            # Calculate motion frequency (events per minute)
            motion_frequency = total_events / minutes
            
            return {
                'total_events': total_events,
                'average_area': average_area,
                'most_active_zone': most_active_zone,
                'motion_frequency': motion_frequency,
                'zone_activity': zone_activity
            }
            
        except Exception as e:
            logger.error(f"Error calculating motion statistics: {e}")
            return {}
    
    def draw_motion_overlay(self, frame: np.ndarray, motion_data: Optional[dict] = None) -> np.ndarray:
        """Draw motion detection overlay on frame"""
        try:
            overlay = frame.copy()
            
            # Draw detection zones
            frame_height, frame_width = frame.shape[:2]
            
            for zone in self.detection_zones:
                zone_name = zone['name']
                roi = zone['roi']
                
                x1 = int(roi[0] * frame_width)
                y1 = int(roi[1] * frame_height)
                x2 = int((roi[0] + roi[2]) * frame_width)
                y2 = int((roi[1] + roi[3]) * frame_height)
                
                # Zone color based on motion
                color = (0, 255, 0)  # Green for no motion
                if motion_data and motion_data['zones'].get(zone_name, {}).get('motion_detected', False):
                    color = (0, 0, 255)  # Red for motion
                
                # Draw zone rectangle
                cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
                
                # Draw zone label
                cv2.putText(overlay, zone_name.upper(), (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Draw motion center if available
            if motion_data and motion_data.get('motion_center'):
                center = motion_data['motion_center']
                cv2.circle(overlay, center, 10, (255, 0, 0), -1)
                cv2.circle(overlay, center, 15, (255, 0, 0), 2)
            
            # Draw motion statistics
            if motion_data:
                stats_text = f"Motion: {motion_data['contour_count']} contours, "
                stats_text += f"Area: {motion_data['total_area']}"
                
                cv2.putText(overlay, stats_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            return overlay
            
        except Exception as e:
            logger.error(f"Error drawing motion overlay: {e}")
            return frame
    
    def reset(self):
        """Reset motion detector state"""
        self.prev_frame = None
        self.motion_history.clear()
        self.last_motion_time = None
        logger.info("Motion detector reset") 