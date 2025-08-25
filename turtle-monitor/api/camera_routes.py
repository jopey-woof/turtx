#!/usr/bin/env python3
"""
🐢 Turtle Camera API Routes
FastAPI routes for camera management and control
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Tuple
from fastapi import APIRouter, HTTPException, Body, Path, Query, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from camera_manager import TurtleCameraManager, IRFilterMode, CameraPreset
from camera_optimizer import camera_optimizer
from simple_camera_controls import camera_controls

logger = logging.getLogger(__name__)

# Create router
camera_router = APIRouter(prefix="/api/camera", tags=["camera"])

# Global camera manager instance
camera_manager: Optional[TurtleCameraManager] = None

def get_camera_manager() -> TurtleCameraManager:
    """Get camera manager instance"""
    global camera_manager
    if not camera_manager:
        raise HTTPException(status_code=503, detail="Camera manager not initialized")
    return camera_manager

# Pydantic models for request/response
class CameraSettingsRequest(BaseModel):
    """Camera settings update request"""
    exposure_mode: Optional[str] = None
    exposure_time: Optional[int] = None
    gain: Optional[int] = None
    white_balance_auto: Optional[bool] = None
    white_balance_temperature: Optional[int] = None
    brightness: Optional[int] = None
    contrast: Optional[int] = None
    saturation: Optional[int] = None
    sharpness: Optional[int] = None

class ResolutionRequest(BaseModel):
    """Resolution change request"""
    width: int
    height: int
    is_streaming: bool = True

class IRFilterRequest(BaseModel):
    """IR filter control request"""
    mode: str  # "auto", "day", "night"

class PresetRequest(BaseModel):
    """Camera preset request"""
    preset: str  # "daylight", "night_vision", "auto", "custom"

@camera_router.get("/status")
async def camera_status():
    """Get camera health and connection status"""
    try:
        camera_mgr = get_camera_manager()
        status = camera_mgr.get_status()
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "camera": status,
            "status": "online" if status.get("connected", False) else "offline"
        }
    except Exception as e:
        logger.error(f"Error getting camera status: {e}")
        raise HTTPException(status_code=500, detail=f"Camera status error: {str(e)}")

@camera_router.get("/capabilities")
async def camera_capabilities():
    """Get camera capabilities and supported features"""
    try:
        camera_mgr = get_camera_manager()
        status = camera_mgr.get_status()
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "capabilities": status.get("capabilities", {}),
            "device": status.get("device", ""),
            "supported_controls": {
                "exposure": {"auto": True, "manual": True, "range": [1, 5000]},
                "gain": {"range": [0, 100]},
                "white_balance": {"auto": True, "manual": True, "temperature_range": [2800, 6500]},
                "brightness": {"range": [-64, 64]},
                "contrast": {"range": [0, 64]},
                "saturation": {"range": [0, 128]},
                "sharpness": {"range": [0, 6]},
                "ir_filter": {"modes": ["auto", "day", "night"]},
                "presets": ["daylight", "night_vision", "auto", "custom"]
            }
        }
    except Exception as e:
        logger.error(f"Error getting camera capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Camera capabilities error: {str(e)}")

@camera_router.get("/live")
async def camera_live():
    """Get current camera frame as JPEG"""
    try:
        camera_mgr = get_camera_manager()
        
        # Start streaming if not already
        if not camera_mgr.is_streaming:
            camera_mgr.start_streaming()
            await asyncio.sleep(0.2)  # Reduced wait time
        
        # Add timeout for frame capture
        jpeg_data = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, camera_mgr.get_current_frame),
            timeout=3.0
        )
        
        if jpeg_data is None:
            raise HTTPException(status_code=503, detail="No camera frame available")
        
        return StreamingResponse(
            iter([jpeg_data]),
            media_type="image/jpeg",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except asyncio.TimeoutError:
        logger.error("Camera live frame timeout")
        raise HTTPException(status_code=503, detail="Camera frame timeout")
    except Exception as e:
        logger.error(f"Error getting camera live frame: {e}")
        raise HTTPException(status_code=500, detail=f"Camera live error: {str(e)}")

@camera_router.get("/live/{resolution}")
async def camera_live_resolution(
    resolution: str = Path(..., description="Resolution: 720p, 1080p, 480p, 240p")
):
    """Get camera frame at specific resolution"""
    try:
        camera_mgr = get_camera_manager()
        
        # Parse resolution
        resolution_map = {
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "480p": (640, 480),
            "240p": (320, 240)
        }
        
        if resolution not in resolution_map:
            raise HTTPException(status_code=400, detail=f"Unsupported resolution: {resolution}")
        
        target_res = resolution_map[resolution]
        
        # Set resolution temporarily
        camera_mgr.set_resolution(target_res, is_streaming=True)
        await asyncio.sleep(0.2)  # Wait for resolution change
        
        jpeg_data = camera_mgr.get_current_frame()
        if jpeg_data is None:
            raise HTTPException(status_code=503, detail="No camera frame available")
        
        return StreamingResponse(
            iter([jpeg_data]),
            media_type="image/jpeg",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except Exception as e:
        logger.error(f"Error getting camera live frame at {resolution}: {e}")
        raise HTTPException(status_code=500, detail=f"Camera live error: {str(e)}")

@camera_router.get("/stream")
async def camera_stream():
    """Get camera MJPEG stream - always available"""
    try:
        camera_mgr = get_camera_manager()
        
        async def generate_frames():
            frame_count = 0
            consecutive_failures = 0
            max_failures = 5
            
            while True:
                try:
                    # Get frame from camera manager
                    jpeg_data = camera_mgr.get_current_frame()
                    
                    if jpeg_data is None or jpeg_data == camera_mgr._get_placeholder_image():
                        consecutive_failures += 1
                        if consecutive_failures > max_failures:
                            # Send placeholder frame after too many failures
                            jpeg_data = camera_mgr._get_placeholder_image()
                            consecutive_failures = 0
                        else:
                            await asyncio.sleep(0.1)  # Short wait before retry
                            continue
                    else:
                        consecutive_failures = 0
                    
                    # MJPEG format: frame boundary + JPEG data
                    frame_data = (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n"
                        b"Content-Length: " + str(len(jpeg_data)).encode() + b"\r\n\r\n" +
                        jpeg_data + b"\r\n"
                    )
                    
                    yield frame_data
                    frame_count += 1
                    
                    # Control frame rate - slower for better reliability
                    await asyncio.sleep(1.0 / 10)  # 10 FPS for stability
                    
                except Exception as e:
                    logger.error(f"Error in camera stream frame {frame_count}: {e}")
                    consecutive_failures += 1
                    
                    # Send placeholder frame on error
                    try:
                        placeholder_data = camera_mgr._get_placeholder_image()
                        frame_data = (
                            b"--frame\r\n"
                            b"Content-Type: image/jpeg\r\n"
                            b"Content-Length: " + str(len(placeholder_data)).encode() + b"\r\n\r\n" +
                            placeholder_data + b"\r\n"
                        )
                        yield frame_data
                    except:
                        pass
                    
                    await asyncio.sleep(1.0)  # Wait before retry
        
        return StreamingResponse(
            generate_frames(),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "Connection": "keep-alive"
            }
        )
    except Exception as e:
        logger.error(f"Error setting up camera stream: {e}")
        raise HTTPException(status_code=500, detail=f"Camera stream error: {str(e)}")

@camera_router.get("/snapshot")
async def camera_snapshot():
    """Get high-quality camera snapshot"""
    try:
        camera_mgr = get_camera_manager()
        
        # Use FFmpeg for maximum quality with timeout
        jpeg_data = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, camera_mgr.capture_ffmpeg_snapshot),
            timeout=5.0
        )
        
        if jpeg_data is None:
            # Fallback to OpenCV with timeout
            jpeg_data = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, camera_mgr.capture_snapshot),
                timeout=3.0
            )
        
        if jpeg_data is None:
            raise HTTPException(status_code=503, detail="Failed to capture camera snapshot")
        
        return StreamingResponse(
            iter([jpeg_data]),
            media_type="image/jpeg",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Content-Disposition": "attachment; filename=turtle_snapshot.jpg"
            }
        )
    except asyncio.TimeoutError:
        logger.error("Camera snapshot timeout")
        raise HTTPException(status_code=503, detail="Camera snapshot timeout")
    except Exception as e:
        logger.error(f"Error getting camera snapshot: {e}")
        raise HTTPException(status_code=500, detail=f"Camera snapshot error: {str(e)}")

@camera_router.get("/snapshot/{resolution}")
async def camera_snapshot_resolution(
    resolution: str = Path(..., description="Resolution: 720p, 1080p, 480p, 240p")
):
    """Get camera snapshot at specific resolution"""
    try:
        camera_mgr = get_camera_manager()
        
        # Parse resolution
        resolution_map = {
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "480p": (640, 480),
            "240p": (320, 240)
        }
        
        if resolution not in resolution_map:
            raise HTTPException(status_code=400, detail=f"Unsupported resolution: {resolution}")
        
        target_res = resolution_map[resolution]
        
        # Capture snapshot at specified resolution
        jpeg_data = camera_mgr.capture_ffmpeg_snapshot(target_res)
        if jpeg_data is None:
            # Fallback to OpenCV
            jpeg_data = camera_mgr.capture_snapshot(target_res)
        
        if jpeg_data is None:
            raise HTTPException(status_code=503, detail="Failed to capture camera snapshot")
        
        return StreamingResponse(
            iter([jpeg_data]),
            media_type="image/jpeg",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Content-Disposition": f"attachment; filename=turtle_snapshot_{resolution}.jpg"
            }
        )
    except Exception as e:
        logger.error(f"Error getting camera snapshot at {resolution}: {e}")
        raise HTTPException(status_code=500, detail=f"Camera snapshot error: {str(e)}")

@camera_router.get("/settings")
async def get_camera_settings():
    """Get current camera settings"""
    try:
        camera_mgr = get_camera_manager()
        status = camera_mgr.get_status()
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "settings": status.get("settings", {}),
            "resolution": status.get("resolution", {})
        }
    except Exception as e:
        logger.error(f"Error getting camera settings: {e}")
        raise HTTPException(status_code=500, detail=f"Camera settings error: {str(e)}")

@camera_router.post("/settings")
async def update_camera_settings(settings: CameraSettingsRequest):
    """Update camera settings"""
    try:
        camera_mgr = get_camera_manager()
        
        # Add timeout for camera operations
        async def update_settings_with_timeout():
            # Update settings
            if settings.exposure_mode is not None:
                camera_mgr.set_exposure(settings.exposure_mode, settings.exposure_time)
            
            if settings.gain is not None:
                camera_mgr.set_gain(settings.gain)
            
            if settings.white_balance_auto is not None:
                camera_mgr.set_white_balance(settings.white_balance_auto, settings.white_balance_temperature)
            
            if any([settings.brightness, settings.contrast, settings.saturation, settings.sharpness]):
                camera_mgr.set_image_quality(
                    brightness=settings.brightness,
                    contrast=settings.contrast,
                    saturation=settings.saturation,
                    sharpness=settings.sharpness
                )
        
        # Run with timeout
        await asyncio.wait_for(update_settings_with_timeout(), timeout=5.0)
        
        # Get updated status
        status = camera_mgr.get_status()
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "success": True,
            "message": "Camera settings updated",
            "settings": status.get("settings", {})
        }
    except asyncio.TimeoutError:
        logger.error("Camera settings update timeout")
        raise HTTPException(status_code=503, detail="Camera settings update timeout")
    except Exception as e:
        logger.error(f"Error updating camera settings: {e}")
        raise HTTPException(status_code=500, detail=f"Camera settings error: {str(e)}")

@camera_router.post("/resolution")
async def set_camera_resolution(resolution: ResolutionRequest):
    """Set camera resolution"""
    try:
        camera_mgr = get_camera_manager()
        
        # Validate resolution
        valid_resolutions = [(1920, 1080), (1280, 720), (640, 480), (320, 240)]
        if (resolution.width, resolution.height) not in valid_resolutions:
            raise HTTPException(status_code=400, detail="Invalid resolution")
        
        camera_mgr.set_resolution((resolution.width, resolution.height), resolution.is_streaming)
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "success": True,
            "message": f"Resolution set to {resolution.width}x{resolution.height}",
            "resolution": {"width": resolution.width, "height": resolution.height}
        }
    except Exception as e:
        logger.error(f"Error setting camera resolution: {e}")
        raise HTTPException(status_code=500, detail=f"Camera resolution error: {str(e)}")

@camera_router.post("/ir-filter")
async def set_ir_filter(request: IRFilterRequest):
    """Set IR filter mode"""
    try:
        camera_mgr = get_camera_manager()
        
        # Parse mode
        mode_map = {
            "auto": IRFilterMode.AUTO,
            "day": IRFilterMode.DAY,
            "night": IRFilterMode.NIGHT
        }
        
        if request.mode not in mode_map:
            raise HTTPException(status_code=400, detail=f"Invalid IR filter mode: {request.mode}")
        
        camera_mgr.set_ir_filter(mode_map[request.mode])
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "success": True,
            "message": f"IR filter set to {request.mode} mode"
        }
    except Exception as e:
        logger.error(f"Error setting IR filter: {e}")
        raise HTTPException(status_code=500, detail=f"IR filter error: {str(e)}")

@camera_router.post("/preset")
async def apply_camera_preset(request: PresetRequest):
    """Apply camera preset configuration"""
    try:
        camera_mgr = get_camera_manager()
        
        # Parse preset
        preset_map = {
            "daylight": CameraPreset.DAYLIGHT,
            "night_vision": CameraPreset.NIGHT_VISION,
            "auto": CameraPreset.AUTO,
            "custom": CameraPreset.CUSTOM
        }
        
        if request.preset not in preset_map:
            raise HTTPException(status_code=400, detail=f"Invalid preset: {request.preset}")
        
        camera_mgr.apply_preset(preset_map[request.preset])
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "success": True,
            "message": f"Camera preset applied: {request.preset}"
        }
    except Exception as e:
        logger.error(f"Error applying camera preset: {e}")
        raise HTTPException(status_code=500, detail=f"Camera preset error: {str(e)}")

@camera_router.get("/restart")
async def restart_camera():
    """Restart camera connection"""
    try:
        camera_mgr = get_camera_manager()
        
        success = camera_mgr.restart()
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "success": success,
            "message": "Camera restart successful" if success else "Camera restart failed"
        }
    except Exception as e:
        logger.error(f"Error restarting camera: {e}")
        raise HTTPException(status_code=500, detail=f"Camera restart error: {str(e)}")

@camera_router.get("/stats")
async def camera_stats():
    """Get camera performance statistics"""
    try:
        camera_mgr = get_camera_manager()
        status = camera_mgr.get_status()
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "performance": {
                "fps": status.get("fps", 0),
                "connected": status.get("connected", False),
                "streaming": status.get("streaming", False),
                "device": status.get("device", ""),
                "resolution": status.get("resolution", {})
            },
            "settings": status.get("settings", {})
        }
    except Exception as e:
        logger.error(f"Error getting camera stats: {e}")
        raise HTTPException(status_code=500, detail=f"Camera stats error: {str(e)}")

# Initialize camera manager
def init_camera_manager():
    """Initialize the camera manager and auto-start streaming"""
    global camera_manager
    try:
        # Initialize camera manager in a non-blocking way
        logger.info("🔄 Initializing camera manager...")
        
        # Create a simple camera manager that doesn't block
        camera_manager = TurtleCameraManager()
        
        # Auto-start streaming for immediate camera availability
        try:
            logger.info("📹 Auto-starting camera stream...")
            camera_manager.start_streaming()
            logger.info("✅ Camera stream auto-started successfully")
        except Exception as stream_error:
            logger.warning(f"⚠️ Auto-start stream failed (will retry): {stream_error}")
        
        logger.info("✅ Camera manager initialized with auto-stream")
        return camera_manager
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize camera manager: {e}")
        camera_manager = None
        # Don't raise exception, just log and continue
        return None

def stop_camera_manager():
    """Stop the camera manager"""
    global camera_manager
    if camera_manager:
        camera_manager.stop()
        camera_manager = None
        logger.info("🛑 Camera manager stopped") 

@camera_router.get("/api/camera/optimize/status")
async def get_camera_optimization_status():
    """Get comprehensive camera optimization status"""
    try:
        status = camera_optimizer.get_status()
        return {
            "success": True,
            "optimizer": status,
            "message": "Camera optimization status retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting optimization status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get optimization status: {e}")

@camera_router.get("/api/camera/optimize/profiles")
async def get_camera_profiles():
    """Get available camera profiles"""
    try:
        profiles = {}
        for name, profile in camera_optimizer.profiles.items():
            profiles[name] = {
                "name": profile.name,
                "description": profile.description,
                "settings": profile.settings,
                "ir_filter": profile.ir_filter
            }
        
        return {
            "success": True,
            "profiles": profiles,
            "message": f"Found {len(profiles)} camera profiles"
        }
    except Exception as e:
        logger.error(f"Error getting camera profiles: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get camera profiles: {e}")

@camera_router.post("/api/camera/optimize/profile/{profile_name}")
async def apply_camera_profile(profile_name: str):
    """Apply a camera profile"""
    try:
        if profile_name not in camera_optimizer.profiles:
            raise HTTPException(status_code=404, detail=f"Profile '{profile_name}' not found")
        
        success = camera_optimizer.apply_profile(profile_name)
        if success:
            return {
                "success": True,
                "profile": profile_name,
                "message": f"Applied camera profile: {profile_name}"
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to apply profile: {profile_name}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying camera profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to apply camera profile: {e}")

@camera_router.post("/api/camera/optimize/auto")
async def auto_optimize_camera():
    """Automatically optimize camera for current conditions"""
    try:
        success = camera_optimizer.optimize_for_conditions()
        if success:
            return {
                "success": True,
                "message": "Camera automatically optimized for current conditions"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to auto-optimize camera")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error auto-optimizing camera: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to auto-optimize camera: {e}")

@camera_router.get("/api/camera/optimize/ir-filter")
async def get_ir_filter_status():
    """Get IR filter status"""
    try:
        ir_status = camera_optimizer.detect_ir_filter()
        return {
            "success": True,
            "ir_filter": ir_status,
            "message": "IR filter status retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting IR filter status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get IR filter status: {e}")

@camera_router.post("/api/camera/optimize/control/{control_id}")
async def set_camera_control(control_id: str, value: int):
    """Set a specific camera control"""
    try:
        success = camera_optimizer.set_control_value(control_id, value)
        if success:
            return {
                "success": True,
                "control": control_id,
                "value": value,
                "message": f"Set {control_id} to {value}"
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to set {control_id} to {value}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting camera control: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set camera control: {e}")

@camera_router.get("/api/camera/optimize/control/{control_id}")
async def get_camera_control(control_id: str):
    """Get current value of a camera control"""
    try:
        value = camera_optimizer.get_control_value(control_id)
        if value is not None:
            control = camera_optimizer.controls.get(control_id)
            return {
                "success": True,
                "control": control_id,
                "value": value,
                "range": f"{control.min_value}-{control.max_value}" if control else None,
                "message": f"Current value of {control_id}: {value}"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Control '{control_id}' not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting camera control: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get camera control: {e}")

@camera_router.post("/api/camera/optimize/profile/custom")
async def create_custom_profile(name: str, description: str, settings: Dict[str, int]):
    """Create a custom camera profile"""
    try:
        success = camera_optimizer.create_custom_profile(name, description, settings)
        if success:
            return {
                "success": True,
                "profile": name,
                "message": f"Created custom profile: {name}"
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to create profile: {name}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating custom profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create custom profile: {e}")

@camera_router.get("/api/camera/optimize/controls")
async def get_all_camera_controls():
    """Get all available camera controls"""
    try:
        controls = {}
        for control_id, control in camera_optimizer.controls.items():
            controls[control_id] = {
                "name": control.name,
                "current_value": control.current_value,
                "range": f"{control.min_value}-{control.max_value}",
                "type": control.control_type,
                "step": control.step,
                "menu_options": control.menu_options
            }
        
        return {
            "success": True,
            "controls": controls,
            "message": f"Found {len(controls)} camera controls"
        }
    except Exception as e:
        logger.error(f"Error getting camera controls: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get camera controls: {e}") 

@camera_router.get("/simple/status")
async def get_simple_camera_status():
    """Get simple camera status with current settings"""
    try:
        status = camera_controls.get_status()
        return {
            "success": True,
            "camera": status,
            "message": "Simple camera status retrieved",
            "turtle_safety": {
                "note": "Camera is for monitoring only - avoid extended use to prevent turtle stress",
                "recommended_use": "Brief monitoring sessions only",
                "ir_warning": "IR lighting can disturb turtles - use sparingly if available"
            }
        }
    except Exception as e:
        logger.error(f"Error getting simple camera status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get camera status: {e}")

@camera_router.post("/simple/profile/turtle-monitor")
async def apply_turtle_monitor_profile():
    """Apply turtle monitoring optimized profile (Turtle-Safe)"""
    try:
        success = camera_controls.apply_turtle_monitor_profile()
        if success:
            return {
                "success": True,
                "profile": "turtle_monitor",
                "message": "Turtle Monitor Profile Applied Successfully",
                "turtle_safety": {
                    "note": "🐢 Camera optimized for turtle habitat monitoring",
                    "warning": "⚠️ Camera is for monitoring only - avoid extended use to prevent turtle stress",
                    "settings": "Optimized for natural, non-disturbing monitoring"
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to apply turtle monitor profile")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying turtle monitor profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to apply profile: {e}")

@camera_router.post("/simple/profile/daylight")
async def apply_daylight_profile():
    """Apply daylight optimized profile"""
    try:
        success = camera_controls.apply_daylight_profile()
        if success:
            return {
                "success": True,
                "profile": "daylight",
                "message": "Daylight Profile Applied Successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to apply daylight profile")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying daylight profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to apply profile: {e}")

@camera_router.post("/simple/profile/low-light")
async def apply_low_light_profile():
    """Apply low light optimized profile"""
    try:
        success = camera_controls.apply_low_light_profile()
        if success:
            return {
                "success": True,
                "profile": "low_light",
                "message": "Low Light Profile Applied Successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to apply low light profile")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying low light profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to apply profile: {e}")

@camera_router.post("/simple/profile/fix-green-tint")
async def apply_green_tint_fix():
    """Apply green tint fix profile"""
    try:
        success = camera_controls.fix_green_tint()
        if success:
            return {
                "success": True,
                "profile": "fix_green_tint",
                "message": "Green Tint Fix Applied Successfully",
                "fix_details": {
                    "white_balance": "Manual mode enabled",
                    "temperature": "Neutral 5000K",
                    "saturation": "Reduced to 70",
                    "hue": "Reset to neutral"
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to apply green tint fix")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying green tint fix: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to apply green tint fix: {e}")

@camera_router.get("/simple/controls")
async def get_all_camera_controls():
    """Get all available camera controls and their current values"""
    try:
        controls = camera_controls.get_all_controls()
        available_controls = camera_controls.available_controls
        
        return {
            "success": True,
            "available_controls": available_controls,
            "current_values": controls,
            "message": f"Found {len(available_controls)} available controls",
            "controls_info": {
                "brightness": "Adjust image brightness (-64 to 64)",
                "contrast": "Adjust image contrast (0 to 64)",
                "saturation": "Adjust color saturation (0 to 128)",
                "hue": "Adjust color hue (-40 to 40)",
                "white_balance_automatic": "Auto white balance (0=off, 1=on)",
                "gamma": "Adjust gamma correction (72 to 500)",
                "gain": "Adjust gain/amplification (0 to 100)",
                "power_line_frequency": "Power line frequency (0=disabled, 1=50Hz, 2=60Hz)",
                "white_balance_temperature": "White balance temperature (2800K to 6500K)",
                "sharpness": "Adjust image sharpness (0 to 6)",
                "backlight_compensation": "Backlight compensation (0 to 2)",
                "auto_exposure": "Auto exposure mode (0=auto, 1=manual, 2=shutter priority, 3=aperture priority)",
                "exposure_time_absolute": "Exposure time in microseconds (1 to 5000)",
                "exposure_dynamic_framerate": "Dynamic framerate adjustment (0=off, 1=on)"
            }
        }
    except Exception as e:
        logger.error(f"Error getting camera controls: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get camera controls: {e}")

@camera_router.get("/simple/ir-filter")
async def get_ir_filter_status():
    """Get IR filter status with turtle safety warning"""
    try:
        ir_status = camera_controls.check_ir_filter()
        return {
            "success": True,
            "ir_filter": ir_status,
            "message": "IR filter status retrieved",
            "turtle_safety": {
                "warning": "⚠️ IR lighting can disturb turtles - use sparingly if available",
                "recommendation": "Use natural lighting when possible for turtle monitoring"
            }
        }
    except Exception as e:
        logger.error(f"Error getting IR filter status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get IR filter status: {e}")

@camera_router.post("/simple/control/{control_name}")
async def set_simple_camera_control(control_name: str, value: int):
    """Set a specific camera control with turtle safety check"""
    try:
        # Check if this is an IR-related control
        ir_controls = ['ir_filter', 'ir_cut_filter', 'night_mode', 'ir_led', 'ir_illuminator', 'ir_light', 'night_vision']
        is_ir_control = any(ir_name in control_name.lower() for ir_name in ir_controls)
        
        success = camera_controls.set_control(control_name, value)
        if success:
            response = {
                "success": True,
                "control": control_name,
                "value": value,
                "message": f"Set {control_name} to {value}"
            }
            
            if is_ir_control:
                response["turtle_safety"] = {
                    "warning": "⚠️ IR control modified - this may affect turtle behavior",
                    "recommendation": "Monitor turtle response and use minimal IR lighting"
                }
            
            return response
        else:
            raise HTTPException(status_code=400, detail=f"Failed to set {control_name} to {value}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting camera control: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set camera control: {e}")

@camera_router.get("/simple/control/{control_name}")
async def get_simple_camera_control(control_name: str):
    """Get current value of a camera control"""
    try:
        value = camera_controls.get_control(control_name)
        if value is not None:
            return {
                "success": True,
                "control": control_name,
                "value": value,
                "message": f"Current value of {control_name}: {value}"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Control '{control_name}' not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting camera control: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get camera control: {e}") 