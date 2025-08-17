#!/usr/bin/env python3
"""
Fixed TEMPerHUM Reader - Uses existing working script
"""

import json
import sys
import time
import os
import subprocess

def read_temperhum_fixed():
    """Read from TEMPerHUM using existing working script"""
    try:
        # Use the existing working script
        script_path = '/home/shrimp/turtle-monitor/hardware/sensors/temperHUM_reader.py'
        if os.path.exists(script_path):
            try:
                # Run with timeout
                result = subprocess.run(['python3', script_path], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and result.stdout.strip():
                    data = json.loads(result.stdout)
                    if data.get('status') == 'success':
                        return data
                    else:
                        return {"error": f"Script failed: {data.get('error', 'Unknown error')}", "status": "script_failed"}
                else:
                    return {"error": f"Script returned: {result.returncode}", "status": "script_error"}
            except subprocess.TimeoutExpired:
                return {"error": "Script timed out", "status": "timeout"}
            except json.JSONDecodeError:
                return {"error": "Invalid JSON from script", "status": "json_error"}
            except Exception as e:
                return {"error": f"Script exception: {str(e)}", "status": "exception"}
        else:
            return {"error": "Script not found", "status": "no_script"}
                
    except Exception as e:
        return {"error": str(e), "status": "exception"}

if __name__ == "__main__":
    result = read_temperhum_fixed()
    print(json.dumps(result)) 